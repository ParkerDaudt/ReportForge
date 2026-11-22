import xml.etree.ElementTree as ET

def parse_burp_xml(file_content: bytes):
    """
    Parse Burp Suite XML and return a list of findings as dicts.
    """
    root = ET.fromstring(file_content)
    findings = []
    for issue in root.findall(".//issue"):
        finding = {
            "name": issue.findtext("name"),
            "severity": issue.findtext("severity"),
            "description": issue.findtext("issueBackground"),
            "cwe": issue.findtext("cwe"),
            "cvss": None,
            "affected_host": issue.findtext("host"),
            "recommendation": issue.findtext("remediationBackground"),
            "evidence": issue.findtext("issueDetail"),
            "references": issue.findtext("references"),
            "status": "draft",
            "cve": None,
            "category": "Web"
        }
        findings.append(finding)
    return findings