from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ReportDTO:
    sections: Dict[str, Any] = field(default_factory=dict)  # Stores content sections like text, graphs
    order: List[str] = field(default_factory=list)  # Order of sections to be rendered in the PDF
    layout_config: Dict[str, Any] = field(default_factory=lambda: {"orientation": "portrait", "margin": 1})  # Layout settings

    def add_section(self, name: str, content: Any):
        self.sections[name] = content

    def set_order(self, section_order: List[str]):
        self.order = section_order

    def configure_layout(self, config: Dict[str, Any]):
        self.layout_config.update(config)

    def get_sections(self) -> Dict[str, Any]:
        return self.sections
