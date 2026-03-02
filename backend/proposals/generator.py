import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime


class ProposalGenerator:
    def __init__(self):
        template_dir = Path(__file__).parent / 'templates'
        css_dir = Path(__file__).parent / 'static'
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.css_path = css_dir / 'proposal.css'

    def generate_html(self, extracted_proposal) -> str:
        """Render proposal HTML from ExtractedProposal model instance."""
        template = self.env.get_template('proposal_base.html')

        context = {
            'ref_number': f"PRO-{datetime.now().strftime('%Y%m%d')}-{str(extracted_proposal.id)[:8]}",
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'subject': extracted_proposal.thread.subject,
            'executive_summary': self._build_executive_summary(extracted_proposal),
            'parties': extracted_proposal.parties or {},
            'product': extracted_proposal.product or {},
            'pricing': extracted_proposal.pricing or {},
            'license_terms': extracted_proposal.license_terms or {},
            'sla_terms': extracted_proposal.sla_terms or {},
            'special_conditions': extracted_proposal.special_conditions or [],
            'ambiguities': extracted_proposal.ambiguities or [],
            'confidence': extracted_proposal.confidence or 'low',
            'acceptance_signal': extracted_proposal.acceptance_signal or '',
            'css_content': self._load_css(),
        }

        return template.render(**context)

    def generate_pdf(self, html_content: str) -> bytes:
        """Convert HTML proposal to PDF bytes via WeasyPrint."""
        html = HTML(string=html_content)
        return html.write_pdf()

    def _build_executive_summary(self, proposal) -> str:
        """Generate a 2-3 sentence executive summary from extracted data."""
        parties = proposal.parties or {}
        product = proposal.product or {}
        pricing = proposal.pricing or {}
        license_terms = proposal.license_terms or {}

        client = parties.get('client_name', 'the client')
        vendor = parties.get('vendor_name', 'the vendor')
        product_name = product.get('name', 'the product/service')
        unit_price = pricing.get('unit_price')
        quantity = pricing.get('quantity')
        total_annual = pricing.get('total_annual_value')
        term_years = license_terms.get('term_years')

        summary_parts = [
            f"This proposal outlines the agreed commercial terms between {client} and {vendor} "
            f"for the procurement of {product_name}, facilitated by Concertiv."
        ]

        if unit_price and quantity:
            price_str = f"${unit_price:,.0f}" if isinstance(unit_price, (int, float)) else str(unit_price)
            summary_parts.append(
                f"The agreed pricing is {price_str} per unit for {quantity} units"
                + (f", totaling ${total_annual:,.0f} annually" if total_annual and isinstance(total_annual, (int, float)) else "")
                + (f" over a {term_years}-year term." if term_years else ".")
            )

        confidence = proposal.confidence or 'low'
        if confidence == 'high':
            summary_parts.append("All parties have explicitly confirmed the terms outlined below.")
        elif confidence == 'medium':
            summary_parts.append("Terms have been substantively agreed, with implied acceptance from all parties.")
        else:
            summary_parts.append("Note: Some terms remain under discussion. Please review flagged ambiguities.")

        return ' '.join(summary_parts)

    def _load_css(self) -> str:
        """Load CSS content for inline embedding in HTML."""
        try:
            with open(self.css_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ''
