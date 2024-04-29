import os
import subprocess

def generate_vuln_report(output_dir):
    grype_html_command = ["grype", "-o", "template", "-t", "templates/html-table.tmpl"]
    #loop over the results directory and generate a report
    report_dir = f"{output_dir}/reports"
    print(f"Generating report in: {report_dir}")
    os.makedirs(report_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        print(f"Checking file: {file}")
        if file.endswith(".json"):
            print(f"Generating report for: {file}")
            report_file = os.path.splitext(file)[0]
            print(f"Report file: {report_file}")
            grype_html_command.extend([f"sbom:{output_dir}/{file}", "--file", f"{report_dir}/{report_file}.html"])
            print(f"Running command: {grype_html_command}")
            subprocess.run(grype_html_command, check=True)
            #reset the command for the next iteration
            grype_html_command = ["grype", "-o", "template", "-t", "templates/html-table.tmpl"]