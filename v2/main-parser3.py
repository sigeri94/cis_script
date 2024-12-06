import xml.etree.ElementTree as ET
import base64

def decode_base64(content):
    """Decode base64 encoded content to string."""
    try:
        return base64.b64decode(content).decode('utf-8')
    except Exception as e:
        return f"Error decoding base64: {e}"

def parse_xml_to_html(control_path, dump_path, output_html_path):
    # Parse control.xml
    control_tree = ET.parse(control_path)
    control_root = control_tree.getroot()

    controls = []
    for control in control_root.findall('control'):
        controls.append({
            'id': control.find('id').text,
            'domain': control.find('domain').text,
            'description': control.find('description').text,
            'recommendation': control.find('recommendation').text,
            'expected_result': decode_base64(control.find('expected_result').text),
            'command': decode_base64(control.find('command').text),
            'mandatory': control.find('mandatory').text
        })

    # Parse dump.xml
    dump_tree = ET.parse(dump_path)
    dump_root = dump_tree.getroot()

    host_info = {
        'CheckedHost': dump_root.find('HostInfo/CheckedHost').text,
        'OS': dump_root.find('HostInfo/OS').text,
        'ExportDate': dump_root.find('HostInfo/ExportDate').text,
        'CurrentUser': dump_root.find('HostInfo/CurrentUser').text,
        'SudoUsed': dump_root.find('HostInfo/SudoUsed').text,
    }

    dumps = []
    for dump in dump_root.findall('Dump'):
        dumps.append({
            'ControlID': dump.find('ControlID').text,
            'Content': decode_base64(dump.find('Content').text),
        })

    # Compare controls with dumps
    compliance_results = []
    for control in controls:
        matching_dump = next((d for d in dumps if d['ControlID'] == control['id']), None)
        current_value = matching_dump['Content'] if matching_dump else "N/A"
        status = "PASS" if control['expected_result'] == current_value else "FAIL"

        compliance_results.append({
            **control,
            'current_value': current_value,
            'status': status
        })

    # Generate HTML
    with open(output_html_path, 'w') as html_file:
        html_file.write("""
        <html>
        <head>
            <title>Compliance Report</title>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                pre { white-space: pre-wrap; word-wrap: break-word; margin: 0; }
                .scrollable { max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 5px; }
                .pass { color: green; font-weight: bold; }
                .fail { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
        """)

        # Host Information Table
        html_file.write("<h1>Host Information</h1>")
        html_file.write("<table><tr><th>Property</th><th>Value</th></tr>")
        for key, value in host_info.items():
            html_file.write(f"<tr><td>{key}</td><td>{value}</td></tr>")
        html_file.write("</table><br>")

        # Compliance Table
        html_file.write("<h1>Compliance Results</h1>")
        html_file.write("""
        <table>
            <tr>
                <th>Control ID</th>
                <th>Domain</th>
                <th>Description</th>
                <th>Running Command</th>
                <th>Output Result</th>
                <th>PASS/FAIL</th>
                <th>Mandatory/Secondary</th>
                <th>Recommendation</th>
            </tr>
        """)
        for result in compliance_results:
            status_class = "pass" if result['status'] == "PASS" else "fail"

            html_file.write("<tr>")
            html_file.write(f"<td width=5%>{result['id']}</td>")
            html_file.write(f"<td width=5%>{result['domain']}</td>")
            html_file.write(f"<td width=15%>{result['description']}</td>")
            html_file.write(f"<td><div class='scrollable'><pre>{result['command']}</pre></div></td>")
            html_file.write(f"<td><div class='scrollable'><pre>{result['current_value']}</pre></div></td>")
            html_file.write(f"<td width=5% class='{status_class}'>{result['status']}</td>")
            html_file.write(f"<td width=5%>{result['mandatory']}</td>")
            recommendation = (
                html_file.write(f"<td width=30%>Already PASS no recommendation needed</td>")
                if result['status'] == "PASS"
                else html_file.write(f"<td width=30%>{result['recommendation']}</td>")
            )
            html_file.write("</tr>")
        html_file.write("</table>")

        html_file.write("</body></html>")

# File paths
control_path = 'control.xml'
dump_path = 'dump.xml'
output_html_path = 'compliance_report.html'

# Generate HTML report
parse_xml_to_html(control_path, dump_path, output_html_path)
print(f"Compliance report generated at: {output_html_path}")
