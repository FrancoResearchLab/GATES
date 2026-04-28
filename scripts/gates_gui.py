#!/usr/bin/env python3
"""
Graphical User Interface for GATK Automated Tool for Exome Sequencing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import signal
from pathlib import Path
import json
from datetime import datetime


class GATESConfigManager:
    """Manages saving and loading of configuration."""

    CONFIG_DIR = Path.home() / ".gates_gui"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self.config = self.load_config()

    def load_config(self):
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {"working_directory": str(Path.cwd())}

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def save_working_directory(self, work_dir):
        self.config["working_directory"] = str(work_dir)
        self.save_config()

    def get_working_directory(self):
        work_dir = self.config.get("working_directory", str(Path.cwd()))
        return work_dir if Path(work_dir).exists() else str(Path.cwd())


class GATESPreprocessTab(ttk.Frame):
    """Tab for preprocessing workflow."""

    def __init__(self, parent, config_manager, output_callback, set_process_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.output_callback = output_callback
        self.set_process_callback = set_process_callback
        self.setup_ui()

    def setup_ui(self):
        input_frame = ttk.LabelFrame(self, text="Input Files", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(input_frame, text="Sample Name:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.sample_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.sample_name_var,
                  width=40).grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="FASTQ (Forward):").grid(
            row=1, column=0, sticky="w", pady=2)
        self.fastq1_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.fastq1_var, width=40,
                  state="readonly").grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_fastq1).grid(
            row=1, column=2, padx=2)

        ttk.Label(input_frame, text="FASTQ (Reverse):").grid(
            row=2, column=0, sticky="w", pady=2)
        self.fastq2_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.fastq2_var, width=40,
                  state="readonly").grid(row=2, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_fastq2).grid(
            row=2, column=2, padx=2)

        ttk.Label(input_frame, text="Reference (FASTA):").grid(
            row=3, column=0, sticky="w", pady=2)
        self.reference_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.reference_var,
                  width=40, state="readonly").grid(row=3, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_reference).grid(
            row=3, column=2, padx=2)

        ttk.Label(input_frame, text="Intervals (BED/VCF):").grid(row=4,
                                                                 column=0, sticky="w", pady=2)
        self.intervals_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.intervals_var,
                  width=40, state="readonly").grid(row=4, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_intervals).grid(
            row=4, column=2, padx=2)

        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(options_frame, text="Supporting Files:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.supp_files_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.supp_files_var,
                  width=40, state="readonly").grid(row=0, column=1, padx=5)
        ttk.Button(options_frame, text="Browse", command=self.browse_supp_files).grid(
            row=0, column=2, padx=2)

        ttk.Label(options_frame, text="Threads:").grid(
            row=1, column=0, sticky="w", pady=2)
        self.threads_var = tk.IntVar(value=4)
        ttk.Spinbox(options_frame, from_=1, to=64, textvariable=self.threads_var,
                    width=10).grid(row=1, column=1, sticky="w", padx=5)

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Verbose Output", variable=self.verbose_var).grid(
            row=2, column=0, sticky="w", pady=2)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Run Preprocessing",
                   command=self.run_preprocess).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

    def browse_fastq1(self):
        file = filedialog.askopenfilename(
            title="Select Forward FASTQ File",
            filetypes=[
                ("FASTQ files", "*.gz *.fastq.gz *.fastq *.fq *.fq.gz"), ("All files", "*")]
        )
        if file:
            self.fastq1_var.set(file)

    def browse_fastq2(self):
        file = filedialog.askopenfilename(
            title="Select Reverse FASTQ File",
            filetypes=[
                ("FASTQ files", "*.gz *.fastq *.fastq.gz *.fq *.fq.gz"), ("All files", "*")]
        )
        if file:
            self.fastq2_var.set(file)

    def browse_reference(self):
        file = filedialog.askopenfilename(
            title="Select Reference FASTA File",
            filetypes=[
                ("FASTA files", "*.fa *.fasta *.fa.gz *.fasta.gz *.fna"), ("All files", "*")]
        )
        if file:
            self.reference_var.set(file)

    def browse_intervals(self):
        file = filedialog.askopenfilename(
            title="Select Intervals File",
            filetypes=[("BED files", "*.bed"), ("VCF files", "*.vcf"),
                       ("Interval files", "*.interval_list *.list *.intervals"), ("All files", "*")]
        )
        if file:
            self.intervals_var.set(file)

    def browse_supp_files(self):
        directory = filedialog.askdirectory(
            title="Select Supporting Files Directory"
        )
        if directory:
            self.supp_files_var.set(directory)

    def validate_inputs(self):
        if not self.sample_name_var.get():
            messagebox.showerror("Validation Error", "Sample name is required")
            return False
        if not self.fastq1_var.get():
            messagebox.showerror("Validation Error",
                                 "Forward FASTQ file is required")
            return False
        if not self.fastq2_var.get():
            messagebox.showerror("Validation Error",
                                 "Reverse FASTQ file is required")
            return False
        if not self.reference_var.get():
            messagebox.showerror("Validation Error",
                                 "Reference file is required")
            return False
        if not self.intervals_var.get():
            messagebox.showerror("Validation Error",
                                 "Interval file is required")
            return False
        return True

    def run_preprocess(self):
        if not self.validate_inputs():
            return
        cmd = [
            "gates", "preprocess",
            "-s", self.sample_name_var.get(),
            "--fastq1", self.fastq1_var.get(),
            "--fastq2", self.fastq2_var.get(),
            "-r", self.reference_var.get(),
            "-i", self.intervals_var.get(),
            "-t", str(self.threads_var.get())
        ]
        if self.supp_files_var.get():
            cmd.extend(["--supp-files", self.supp_files_var.get()])
        if self.verbose_var.get():
            cmd.append("-v")
        work_dir = self.config_manager.get_working_directory()
        messagebox.showinfo(
            message="Preprocessing is now running", detail="Monitor progress in the Terminal Output panel.")
        threading.Thread(target=self._run_command, args=(
            cmd, work_dir), daemon=True).start()

    def _run_command(self, cmd, work_dir):
        try:
            cmd_str = " ".join(cmd)
            full_cmd = f"""
eval "$(conda shell.bash hook)"
conda activate gates
{cmd_str}
"""
            process = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=work_dir,
                env=os.environ.copy(),
                preexec_fn=os.setsid
            )
            self.set_process_callback(process)
            for line in process.stdout:
                self.output_callback(line)
            process.wait()
            self.set_process_callback(None)
            if process.returncode == 0:
                messagebox.showinfo(
                    "Success", "Preprocessing completed successfully!")
            elif process.returncode == -signal.SIGTERM:
                self.output_callback("\n[Process terminated by user.]\n")
            else:
                messagebox.showerror(
                    "Error", "Command failed. See terminal output for details.")
        except Exception as e:
            self.set_process_callback(None)
            self.output_callback(f"Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to run command:\n{str(e)}")

    def clear_all(self):
        self.sample_name_var.set("")
        self.fastq1_var.set("")
        self.fastq2_var.set("")
        self.reference_var.set("")
        self.intervals_var.set("")
        self.supp_files_var.set("")
        self.threads_var.set(4)
        self.verbose_var.set(False)


class GATESCallTab(ttk.Frame):
    """Tab for variant calling workflow."""

    def __init__(self, parent, config_manager, output_callback, set_process_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.output_callback = output_callback
        self.set_process_callback = set_process_callback
        self.mode_var = tk.StringVar(value="tumor-only")
        self.setup_ui()

    def setup_ui(self):
        mode_frame = ttk.LabelFrame(self, text="Analysis Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Radiobutton(mode_frame, text="Tumor-Only", variable=self.mode_var,
                        value="tumor-only", command=self.update_ui).pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Tumor-Normal", variable=self.mode_var,
                        value="tumor-normal", command=self.update_ui).pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Germline", variable=self.mode_var,
                        value="germline", command=self.update_ui).pack(anchor=tk.W, pady=1)

        input_frame = ttk.LabelFrame(self, text="Input Files", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(input_frame, text="Tumor BAM:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.tumor_bam_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.tumor_bam_var,
                  width=40, state="readonly").grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_tumor_bam).grid(
            row=0, column=2, padx=2)

        ttk.Label(input_frame, text="Normal BAM:").grid(
            row=1, column=0, sticky="w", pady=2)
        self.normal_bam_var = tk.StringVar()
        self.normal_bam_entry = ttk.Entry(
            input_frame, textvariable=self.normal_bam_var, width=40, state="readonly")
        self.normal_bam_entry.grid(row=1, column=1, padx=5)
        self.normal_bam_button = ttk.Button(
            input_frame, text="Browse", command=self.browse_normal_bam)
        self.normal_bam_button.grid(row=1, column=2, padx=2)

        ttk.Label(input_frame, text="Reference (FASTA):").grid(
            row=2, column=0, sticky="w", pady=2)
        self.reference_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.reference_var,
                  width=40, state="readonly").grid(row=2, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_reference).grid(
            row=2, column=2, padx=2)

        ttk.Label(input_frame, text="Intervals (BED/VCF):").grid(row=3,
                                                                 column=0, sticky="w", pady=2)
        self.intervals_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.intervals_var,
                  width=40, state="readonly").grid(row=3, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_intervals).grid(
            row=3, column=2, padx=2)

        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(options_frame, text="Supporting Files:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.supp_files_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.supp_files_var,
                  width=40, state="readonly").grid(row=0, column=1, padx=5)
        ttk.Button(options_frame, text="Browse", command=self.browse_supp_files).grid(
            row=0, column=2, padx=2)

        ttk.Label(options_frame, text="Threads:").grid(
            row=1, column=0, sticky="w", pady=2)
        self.threads_var = tk.IntVar(value=4)
        ttk.Spinbox(options_frame, from_=1, to=64, textvariable=self.threads_var,
                    width=10).grid(row=1, column=1, sticky="w", padx=5)

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Verbose Output", variable=self.verbose_var).grid(
            row=2, column=0, sticky="w", pady=2)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Run Variant Calling",
                   command=self.run_call).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

        self.update_ui()

    def update_ui(self):
        mode = self.mode_var.get()
        if mode == "tumor-normal":
            self.normal_bam_entry.grid()
            self.normal_bam_button.grid()
        else:
            self.normal_bam_entry.grid_remove()
            self.normal_bam_button.grid_remove()

    def browse_tumor_bam(self):
        file = filedialog.askopenfilename(
            title="Select Tumor BAM File",
            filetypes=[("BAM files", "*.bam"), ("All files", "*")]
        )
        if file:
            self.tumor_bam_var.set(file)

    def browse_normal_bam(self):
        file = filedialog.askopenfilename(
            title="Select Normal BAM File",
            filetypes=[("BAM files", "*.bam"), ("All files", "*")]
        )
        if file:
            self.normal_bam_var.set(file)

    def browse_reference(self):
        file = filedialog.askopenfilename(
            title="Select Reference FASTA File",
            filetypes=[
                ("FASTA files", "*.fa *.fasta *.fa.gz *.fasta.gz"), ("All files", "*")]
        )
        if file:
            self.reference_var.set(file)

    def browse_intervals(self):
        file = filedialog.askopenfilename(
            title="Select Intervals File",
            filetypes=[("BED files", "*.bed"), ("VCF files", "*.vcf"),
                       ("Interval files", "*.interval_list *.list *.intervals"), ("All files", "*")]
        )
        if file:
            self.intervals_var.set(file)

    def browse_supp_files(self):
        directory = filedialog.askdirectory(
            title="Select Supporting Files Directory"
        )
        if directory:
            self.supp_files_var.set(directory)

    def validate_inputs(self):
        if not self.tumor_bam_var.get():
            messagebox.showerror("Validation Error",
                                 "Tumor BAM file is required")
            return False
        if self.mode_var.get() == "tumor-normal" and not self.normal_bam_var.get():
            messagebox.showerror(
                "Validation Error", "Normal BAM file is required for tumor-normal mode")
            return False
        if not self.reference_var.get():
            messagebox.showerror("Validation Error",
                                 "Reference file is required")
            return False
        if not self.intervals_var.get():
            messagebox.showerror("Validation Error",
                                 "Intervals file is required")
            return False
        return True

    def run_call(self):
        if not self.validate_inputs():
            return
        cmd = [
            "gates", "call",
            "--tumor-bam", self.tumor_bam_var.get(),
            "-r", self.reference_var.get(),
            "-m", self.mode_var.get(),
            "-i", self.intervals_var.get(),
            "-t", str(self.threads_var.get())
        ]
        if self.mode_var.get() == "tumor-normal":
            cmd.extend(["--normal-bam", self.normal_bam_var.get()])
        if self.supp_files_var.get():
            cmd.extend(["--supp-files", self.supp_files_var.get()])
        if self.verbose_var.get():
            cmd.append("-v")
        work_dir = self.config_manager.get_working_directory()
        messagebox.showinfo(
            message="Variant Calling is now running",
            detail="Monitor progress in the Terminal Output panel.")
        threading.Thread(target=self._run_command, args=(
            cmd, work_dir), daemon=True).start()

    def _run_command(self, cmd, work_dir):
        try:
            cmd_str = " ".join(cmd)
            full_cmd = f"""
eval "$(conda shell.bash hook)"
conda activate gates
{cmd_str}
"""
            process = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=work_dir,
                env=os.environ.copy(),
                preexec_fn=os.setsid
            )
            self.set_process_callback(process)
            for line in process.stdout:
                self.output_callback(line)
            process.wait()
            self.set_process_callback(None)
            if process.returncode == 0:
                messagebox.showinfo(
                    "Success", "Variant calling completed successfully!")
            elif process.returncode == -signal.SIGTERM:
                self.output_callback("\n[Process terminated by user.]\n")
            else:
                messagebox.showerror(
                    "Error", "Command failed. See terminal output for details.")
        except Exception as e:
            self.set_process_callback(None)
            self.output_callback(f"Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to run command:\n{str(e)}")

    def clear_all(self):
        self.tumor_bam_var.set("")
        self.normal_bam_var.set("")
        self.reference_var.set("")
        self.intervals_var.set("")
        self.supp_files_var.set("")
        self.threads_var.set(4)
        self.verbose_var.set(False)


class GATESAnnotateTab(ttk.Frame):
    """Tab for variant annotation workflow."""

    def __init__(self, parent, config_manager, output_callback, set_process_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.output_callback = output_callback
        self.set_process_callback = set_process_callback
        self.mode_var = tk.StringVar(value="tumor-only")
        self.setup_ui()

    def setup_ui(self):
        mode_frame = ttk.LabelFrame(
            self, text="Analysis Mode (from calling)", padding=10)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Radiobutton(mode_frame, text="Tumor-Only",
                        variable=self.mode_var, value="tumor-only").pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Tumor-Normal",
                        variable=self.mode_var, value="tumor-normal").pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Germline",
                        variable=self.mode_var, value="germline").pack(anchor=tk.W, pady=1)

        input_frame = ttk.LabelFrame(self, text="Input Files", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(input_frame, text="Sample Name:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.sample_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.sample_name_var,
                  width=40).grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="VCF File:").grid(
            row=1, column=0, sticky="w", pady=2)
        self.vcf_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.vcf_var, width=40,
                  state="readonly").grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_vcf).grid(
            row=1, column=2, padx=2)

        ttk.Label(input_frame, text="VEP Cache Directory:").grid(
            row=2, column=0, sticky="w", pady=2)
        self.cache_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.cache_var, width=40,
                  state="readonly").grid(row=2, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_cache).grid(
            row=2, column=2, padx=2)

        ttk.Label(input_frame, text="Reference (FASTA):").grid(
            row=3, column=0, sticky="w", pady=2)
        self.reference_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.reference_var,
                  width=40, state="readonly").grid(row=3, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_reference).grid(
            row=3, column=2, padx=2)

        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)

        ttk.Label(options_frame, text="Max Population AF:").grid(
            row=0, column=0, sticky="w", pady=2)
        self.pop_af_var = tk.DoubleVar(value=0.01)
        ttk.Spinbox(options_frame, from_=0.0, to=1.0, increment=0.001,
                    textvariable=self.pop_af_var, width=10).grid(row=0, column=1, sticky="w", padx=5)

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Verbose Output", variable=self.verbose_var).grid(
            row=1, column=0, sticky="w", pady=2)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Run Annotation",
                   command=self.run_annotate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

    def browse_vcf(self):
        file = filedialog.askopenfilename(
            title="Select VCF File",
            filetypes=[("VCF files", "*.vcf *.vcf.gz"), ("All files", "*")]
        )
        if file:
            self.vcf_var.set(file)

    def browse_cache(self):
        directory = filedialog.askdirectory(title="Select VEP Cache Directory")
        if directory:
            self.cache_var.set(directory)

    def browse_reference(self):
        file = filedialog.askopenfilename(
            title="Select Reference FASTA File",
            filetypes=[
                ("FASTA files", "*.fa *.fasta *.fa.gz *.fasta.gz"), ("All files", "*")]
        )
        if file:
            self.reference_var.set(file)

    def validate_inputs(self):
        if not self.sample_name_var.get():
            messagebox.showerror("Validation Error", "Sample name is required")
            return False
        if not self.vcf_var.get():
            messagebox.showerror("Validation Error", "VCF file is required")
            return False
        if not self.cache_var.get():
            messagebox.showerror("Validation Error",
                                 "VEP cache directory is required")
            return False
        if not self.reference_var.get():
            messagebox.showerror("Validation Error",
                                 "Reference file is required")
            return False
        return True

    def run_annotate(self):
        if not self.validate_inputs():
            return
        cmd = [
            "gates", "annotate",
            "-s", self.sample_name_var.get(),
            "--vcf", self.vcf_var.get(),
            "-m", self.mode_var.get(),
            "-c", self.cache_var.get(),
            "-r", self.reference_var.get(),
            "-a", str(self.pop_af_var.get())
        ]
        if self.verbose_var.get():
            cmd.append("-v")
        work_dir = self.config_manager.get_working_directory()
        messagebox.showinfo(
            message="Annotation is now running",
            detail="Monitor progress in the Terminal Output panel.")
        threading.Thread(target=self._run_command, args=(
            cmd, work_dir), daemon=True).start()

    def _run_command(self, cmd, work_dir):
        try:
            cmd_str = " ".join(cmd)
            full_cmd = f"""
eval "$(conda shell.bash hook)"
conda activate gates
{cmd_str}
"""
            process = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=work_dir,
                env=os.environ.copy(),
                preexec_fn=os.setsid
            )
            self.set_process_callback(process)
            for line in process.stdout:
                self.output_callback(line)
            process.wait()
            self.set_process_callback(None)
            if process.returncode == 0:
                messagebox.showinfo(
                    "Success", "Annotation completed successfully!")
            elif process.returncode == -signal.SIGTERM:
                self.output_callback("\n[Process terminated by user.]\n")
            else:
                messagebox.showerror(
                    "Error", "Command failed. See terminal output for details.")
        except Exception as e:
            self.set_process_callback(None)
            self.output_callback(f"Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to run command:\n{str(e)}")

    def clear_all(self):
        self.sample_name_var.set("")
        self.vcf_var.set("")
        self.cache_var.set("")
        self.reference_var.set("")
        self.pop_af_var.set(0.01)
        self.verbose_var.set(False)


class GATESGUIApp(tk.Tk):
    """Main GATES GUI application."""

    def __init__(self):
        super().__init__()
        self.title("GATES")
        self.geometry("800x950")
        self.config_manager = GATESConfigManager()
        self.current_process = None
        self.setup_ui()

    def set_process(self, process):
        """Store the current running process and update the kill button state."""
        self.current_process = process
        if process is not None:
            self.kill_button.configure(state="normal")
        else:
            self.kill_button.configure(state="disabled")

    def kill_process(self):
        """Kill the currently running process group."""
        if self.current_process is not None:
            try:
                os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                self.append_output("\n[Process terminated by user.]\n")
            except Exception as e:
                self.append_output(
                    f"\n[Failed to terminate process: {str(e)}]\n")
            finally:
                self.current_process = None
                self.kill_button.configure(state="disabled")

    def setup_ui(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Working Directory",
                              command=self.change_working_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About GATES", menu=about_menu)
        about_menu.add_command(label="Version", command=self.show_version)
        about_menu.add_command(label="Citation", command=self.show_citation)
        about_menu.add_command(label="Author", command=self.show_author)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True,
                        padx=10, pady=2)

        title_label = ttk.Label(
            main_frame,
            text="GATES: GATK Automated Tool for Exome Sequencing",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=7)

        work_dir_frame = ttk.LabelFrame(
            main_frame, text="Working Directory", padding=5)
        work_dir_frame.pack(fill=tk.X, padx=5, pady=2)

        self.work_dir_var = tk.StringVar(
            value=self.config_manager.get_working_directory())
        ttk.Label(work_dir_frame, text="Current: ").pack(side=tk.LEFT, padx=5)
        ttk.Label(work_dir_frame, textvariable=self.work_dir_var,
                  wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(work_dir_frame, text="Change",
                   command=self.change_working_directory).pack(side=tk.RIGHT, padx=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Output panel
        output_frame = ttk.LabelFrame(
            main_frame, text="Terminal Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=False, pady=2)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=7, state="disabled",
            font=("Courier", 11), background="#1e1e1e", foreground="#d4d4d4",
            wrap=tk.NONE
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Button row below output
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.pack(fill=tk.X, pady=(4, 0))

        self.kill_button = ttk.Button(
            output_btn_frame, text="Kill Process",
            command=self.kill_process, state="disabled"
        )
        self.kill_button.pack(side=tk.LEFT, padx=2)

        ttk.Button(output_btn_frame, text="Clear",
                   command=self.clear_output).pack(side=tk.RIGHT, padx=2)

        # Add tabs
        self.preprocess_tab = GATESPreprocessTab(
            self.notebook, self.config_manager, self.append_output, self.set_process)
        self.notebook.add(self.preprocess_tab, text="Preprocessing")

        self.call_tab = GATESCallTab(
            self.notebook, self.config_manager, self.append_output, self.set_process)
        self.notebook.add(self.call_tab, text="Variant Calling")

        self.annotate_tab = GATESAnnotateTab(
            self.notebook, self.config_manager, self.append_output, self.set_process)
        self.notebook.add(self.annotate_tab, text="Annotation")

    def append_output(self, text):
        """Append text to the output panel (thread-safe)."""
        self.output_text.configure(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.configure(state="disabled")

    def clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state="disabled")

    def change_working_directory(self):
        directory = filedialog.askdirectory(
            title="Select Working Directory",
            initialdir=self.config_manager.get_working_directory()
        )
        if directory:
            self.config_manager.save_working_directory(directory)
            self.work_dir_var.set(directory)
            messagebox.showinfo(
                "Success", f"Working directory changed to:\n{directory}")

    def show_version(self):
        messagebox.showinfo(
            message="Version",
            detail="v1.3.0"
        )

    def show_citation(self):
        messagebox.showinfo(
            message="Citation",
            detail="Bambach, NE (2026). GATES: GATK Automated Tool for Exome Sequencing v1.3.0. Github. https://github.com/FrancoResearchLab/GATES."
        )

    def show_author(self):
        messagebox.showinfo(
            message="Nicholas E. Bambach",
            detail="bambachn1@chop.edu"
        )


if __name__ == "__main__":
    app = GATESGUIApp()
    app.mainloop()
