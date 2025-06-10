import xml.etree.ElementTree as ET

def parse_nessus_xml(file_content: bytes):
    """
    Parse Nessus XML and return a list of findings as dicts.
    """
    root = ET.fromstring(file_content)
    findings = []
    for report_item in root.findall(".//ReportItem"):
        finding = {
            "name": report_item.attrib.get("pluginName"),
            "severity": report_item.attrib.get("severity"),
            "description": report_item.findtext("description"),
            "cve": report_item.findtext("cve"),
            "cwe": report_item.findtext("cwe"),
            "cvss": float(report_item.findtext("cvss_base_score") or 0) if report_item.findtext("cvss_base_score") else None,
            "affected_host": report_item.attrib.get("host"),
            "recommendation": report_item.findtext("solution"),
            "evidence": report_item.findtext("plugin_output"),
            "references": report_item.findtext("see_also"),
            "status": "draft",
            "category": "Infrastructure"
        }
        findings.append(finding)
    return findings