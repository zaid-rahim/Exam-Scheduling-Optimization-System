# 📅 Exam Scheduling Optimization System

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-lightgrey?logo=pandas)
![Optimization](https://img.shields.io/badge/Algorithm-Simulated%20Annealing-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 📖 Description

This project implements an **optimized exam scheduling system** that automatically assigns courses to exam slots while minimizing student conflicts.

The system uses:

* 📊 **Data processing with Pandas**
* ⚙️ **Heuristic-based initial scheduling**
* 🔥 **Simulated Annealing optimization**

It ensures:

* Minimal students having **3 or more exams in a single day**
* Reduced **consecutive exam stress**
* Balanced **slot capacity utilization**

---

## 🎯 Problem Statement

Manual exam scheduling is complex and often leads to:

* Student overload (multiple exams in one day)
* Consecutive exams without breaks
* Poor slot utilization

This project solves these issues using optimization techniques.

---

## ✨ Features

* 📥 Reads student-course data from Excel
* 🧠 Intelligent initial scheduling algorithm
* 🔄 Advanced optimization using Simulated Annealing
* 📉 Reduces:

  * 3+ exams per day
  * Consecutive exam sequences
* 📊 Generates:

  * Final schedule (CSV)
  * Detailed performance report (TXT)

---

## 🧱 Project Structure

```bash id="8n8h0q"
├── schec_exam.py              # Main scheduling + optimization script
├── input.xlsx                 # Input dataset (student-course mapping)
├── final_output/
│   ├── schedule_final_optimized.csv
│   └── schedule_report_final.txt
```

---

## ⚙️ Requirements

Install dependencies:

```bash id="q0p4gi"
pip install pandas openpyxl
```

---

## 📥 Input Format

The input Excel file should include columns like:

* Student Roll Number
* Course Code
* Course Name
* Section (optional)

The system automatically detects column names.

---

## ▶️ How to Run

```bash id="9y4qzk"
python schec_exam.py --input input.xlsx --outdir ./output --capacity 500
```

### Parameters:

* `--input` → Path to Excel file
* `--outdir` → Output folder
* `--capacity` → Max students per slot

---

## ⚙️ How It Works

### 1️⃣ Data Processing

* Detects relevant columns automatically
* Builds mappings:

  * Course → Students
  * Student → Courses

### 2️⃣ Initial Scheduling

* Assigns courses to slots using heuristics
* Avoids conflicts and capacity overflow

### 3️⃣ Optimization (Core)

Uses **Simulated Annealing** to:

* Reduce overload students
* Minimize consecutive exams
* Improve overall schedule quality

Reference: 

---

## 📊 Output Files

### 📄 schedule_final_optimized.csv

* Course assignment per slot
* Day & slot number
* Enrollment count

### 📑 schedule_report_final.txt

* Before vs After comparison
* Overload reduction stats
* Slot utilization
* Consecutive exam analysis

---

## 📈 Example Results

```id="s3k2d1"
Students with 3+ exams/day: 120 → 25
Students with consecutive exams: 80 → 15
```

---

## 🚀 Future Improvements

* 🌐 Web-based interface (React + Flask)
* 📊 Visualization dashboards
* 🧠 Genetic Algorithm / AI-based optimization
* 📅 Dynamic scheduling with constraints

---

## 👨‍💻 Author

**Zaid Rahim**

---

## ⭐ Why This Project Matters

This project demonstrates:

* Strong problem-solving skills
* Real-world optimization techniques
* Efficient algorithm design
* Data handling at scale

---

## ⭐ Support

If you find this useful, give it a star ⭐ on GitHub!
