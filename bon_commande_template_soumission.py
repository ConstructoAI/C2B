"""
Template HTML pour les bons de commande - Style identique aux soumissions
Utilise le même design professionnel bleu/gris que les soumissions
"""

def generate_soumission_style_html(data, company):
    """Génère le HTML du bon de commande avec le style exact des soumissions"""

    # Créer le tableau des items
    items_html = ""
    for i, item in enumerate(data['items'], 1):
        items_html += f"""
        <tr>
            <td>
                <div class="item-title">{item['description']}</div>
                {f'<div class="item-description">{item["details"]}</div>' if item.get('details') else ''}
            </td>
            <td class="text-center">{item['quantite']} {item['unite']}</td>
            <td class="text-right">{item['prix_unitaire']:,.2f} $</td>
            <td class="text-right"><strong>{item['total']:,.2f} $</strong></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bon de Commande {data['numero']} - {company['name']}</title>
        <style>
            /* Variables CSS */
            :root {{
                --primary-color: #374151;
                --primary-light: #4b5563;
                --primary-dark: #3b82f6;
                --primary-bg: #f9fafb;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
                --transition-base: all 0.3s ease;
            }}

            /* Reset et Base */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                font-size: 10px;
                line-height: 1.3;
                color: #333;
                background: #f5f5f5;
                min-height: 100vh;
            }}

            /* Conteneur principal */
            .container {{
                max-width: 8.5in;
                margin: 20px auto;
                background: white;
                box-shadow: var(--shadow-lg);
                padding: 0.4in;
                position: relative;
            }}

            @media print {{
                body {{ background: white; }}
                .container {{
                    margin: 0;
                    box-shadow: none;
                    padding: 0.3in;
                    max-width: 100%;
                }}
                .no-print {{ display: none !important; }}
                .page-break {{ page-break-before: always; }}
            }}

            /* Header avec gradient */
            .header-gradient {{
                background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
                color: white;
                padding: 30px;
                margin: -0.4in -0.4in 20px -0.4in;
                text-align: center;
                box-shadow: var(--shadow-md);
            }}

            .header-gradient h1 {{
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}

            .header-gradient h2 {{
                font-size: 16px;
                font-weight: 400;
                opacity: 0.95;
                margin-bottom: 5px;
            }}

            .header-gradient .numero {{
                font-size: 14px;
                opacity: 0.9;
                margin-top: 10px;
                font-weight: 500;
            }}

            /* Informations entreprise */
            .company-header {{
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 15px;
                margin-bottom: 20px;
                text-align: right;
            }}

            .company-info {{
                font-size: 10px;
                line-height: 1.4;
                color: #555;
            }}

            .company-info strong {{
                color: var(--primary-dark);
                font-size: 12px;
            }}

            /* Boîtes d'information */
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-bottom: 25px;
            }}

            .info-box {{
                background: var(--primary-bg);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid var(--primary-color);
                box-shadow: var(--shadow-sm);
            }}

            .info-box h3 {{
                color: var(--primary-dark);
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .info-box p {{
                font-size: 10px;
                line-height: 1.4;
                color: #444;
                margin: 3px 0;
            }}

            .info-box p strong {{
                color: var(--primary-dark);
                font-weight: 600;
            }}

            /* Tableau principal */
            .table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin: 20px 0;
                box-shadow: var(--shadow-sm);
                border-radius: 8px;
                overflow: hidden;
            }}

            .table-header {{
                background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
                color: white;
            }}

            .table-header th {{
                padding: 10px 8px;
                font-size: 10px;
                font-weight: 600;
                text-align: left;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border-bottom: none;
            }}

            .table-header th:nth-child(1) {{ width: 50%; }}
            .table-header th:nth-child(2) {{ width: 12%; text-align: center; }}
            .table-header th:nth-child(3) {{ width: 19%; text-align: right; }}
            .table-header th:nth-child(4) {{ width: 19%; text-align: right; }}

            .table td {{
                padding: 6px 8px;
                font-size: 10px;
                border-bottom: 1px solid #e5e7eb;
                vertical-align: top;
            }}

            .table tr:hover {{
                background: rgba(75, 85, 99, 0.02);
            }}

            /* Styles de lignes spéciales */
            .subtotal-row td {{
                background: #f3f4f6;
                font-weight: bold;
                padding: 8px !important;
                color: var(--primary-color);
                border-top: 1px solid #e5e7eb;
            }}

            .total-row td {{
                background: var(--primary-bg);
                font-weight: bold;
                font-size: 11px;
                padding: 10px 8px;
                border-top: 2px solid var(--primary-color);
            }}

            .grand-total-row td {{
                background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 8px;
                border: none;
            }}

            /* Descriptions d'items */
            .item-title {{
                font-weight: 600;
                color: #222;
                font-size: 10px;
                margin-bottom: 2px;
            }}

            .item-description {{
                font-size: 9px;
                color: #666;
                font-style: italic;
                line-height: 1.3;
                margin-top: 2px;
            }}

            /* Alignements */
            .text-center {{ text-align: center; }}
            .text-right {{ text-align: right; }}
            .text-left {{ text-align: left; }}

            /* Pied de page */
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid var(--primary-color);
                text-align: center;
            }}

            .footer-info {{
                font-size: 9px;
                color: #666;
                line-height: 1.4;
                margin: 5px 0;
            }}

            .footer-info strong {{
                color: var(--primary-color);
                font-weight: 600;
            }}

            /* Signatures */
            .signature-section {{
                margin: 30px 0;
                padding: 20px;
                background: var(--primary-bg);
                border-radius: 8px;
            }}

            .signature-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 40px;
                margin-top: 40px;
            }}

            .signature-box {{
                text-align: center;
            }}

            .signature-line {{
                border-top: 2px solid var(--primary-color);
                margin: 0 0 8px 0;
            }}

            .signature-label {{
                font-size: 10px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            /* Badge statut */
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                font-size: 11px;
                font-weight: 500;
                margin-bottom: 10px;
            }}

            /* Conditions */
            .conditions-box {{
                margin-top: 30px;
                padding: 15px;
                background: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 8px;
            }}

            .conditions-box h4 {{
                color: #d97706;
                font-size: 11px;
                margin-bottom: 8px;
                font-weight: 600;
            }}

            .conditions-box p {{
                font-size: 9px;
                color: #92400e;
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header avec gradient bleu -->
            <div class="header-gradient">
                <div class="status-badge">BON DE COMMANDE</div>
                <h1>BON DE COMMANDE</h1>
                <h2>{company['name']}</h2>
                <div class="numero">No. {data['numero']} | Date: {data['date']}</div>
            </div>

            <!-- Informations de l'entreprise -->
            <div class="company-header">
                <div class="company-info">
                    <strong>{company['name']}</strong><br>
                    {company['address']}, {company['city']}, {company['province']} {company['postal_code']}<br>
                    Tél: {company['phone']} | Courriel: {company['email']}<br>
                    RBQ: {company['rbq']} | NEQ: {company['neq']}<br>
                    TPS: {company['tps']} | TVQ: {company['tvq']}
                </div>
            </div>

            <!-- Informations fournisseur et projet -->
            <div class="info-grid">
                <div class="info-box">
                    <h3>Fournisseur</h3>
                    <p><strong>{data['fournisseur']['nom']}</strong></p>
                    {f'<p>Contact: {data["fournisseur"]["contact"]}</p>' if data['fournisseur'].get('contact') else ''}
                    {f'<p>Tél: {data["fournisseur"]["telephone"]}</p>' if data['fournisseur'].get('telephone') else ''}
                    {f'<p>Courriel: {data["fournisseur"]["email"]}</p>' if data['fournisseur'].get('email') else ''}
                    {f'<p>Adresse: {data["fournisseur"]["adresse"]}</p>' if data['fournisseur'].get('adresse') else ''}
                </div>

                <div class="info-box">
                    <h3>Projet</h3>
                    <p><strong>Client:</strong> {data['client']['nom']}</p>
                    <p><strong>Projet:</strong> {data['projet']['nom']}</p>
                    {f'<p><strong>Adresse:</strong> {data["projet"]["adresse"]}</p>' if data['projet'].get('adresse') else ''}
                    {f'<p><strong>Réf. Soumission:</strong> {data["projet"]["ref_soumission"]}</p>' if data['projet'].get('ref_soumission') else ''}
                </div>
            </div>

            <!-- Conditions de paiement et livraison -->
            {f'''<div class="info-grid">
                <div class="info-box">
                    <h3>Conditions</h3>
                    <p><strong>Paiement:</strong> {data.get('conditions_paiement', 'Net 30 jours')}</p>
                    <p><strong>Livraison:</strong> {data.get('date_livraison', 'À déterminer')}</p>
                    <p><strong>Lieu:</strong> {data.get('lieu_livraison', 'Sur le chantier')}</p>
                </div>
                <div class="info-box">
                    <h3>Référence</h3>
                    <p><strong>Date émission:</strong> {data['date']}</p>
                    <p><strong>Validité:</strong> 30 jours</p>
                    <p><strong>Approuvé par:</strong> À compléter</p>
                </div>
            </div>''' if data.get('conditions_paiement') or data.get('date_livraison') else ''}

            <!-- Tableau des articles -->
            <table class="table">
                <thead class="table-header">
                    <tr>
                        <th>Description</th>
                        <th>Quantité</th>
                        <th>Prix Unitaire</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
                <tfoot>
                    <tr class="subtotal-row">
                        <td colspan="3" class="text-right">Sous-total:</td>
                        <td class="text-right">{data['totaux']['sous_total']:,.2f} $</td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="3" class="text-right">TPS (5%):</td>
                        <td class="text-right">{data['totaux']['tps']:,.2f} $</td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="3" class="text-right">TVQ (9.975%):</td>
                        <td class="text-right">{data['totaux']['tvq']:,.2f} $</td>
                    </tr>
                    <tr class="grand-total-row">
                        <td colspan="3" class="text-right">MONTANT TOTAL:</td>
                        <td class="text-right">{data['totaux']['total']:,.2f} $</td>
                    </tr>
                </tfoot>
            </table>

            <!-- Notes et conditions -->
            {f'''<div class="conditions-box">
                <h4>Notes et Instructions</h4>
                <p>{data.get('notes', 'Veuillez confirmer la réception de ce bon de commande.')}</p>
            </div>''' if data.get('notes') else ''}

            <!-- Signatures -->
            <div class="signature-section">
                <h3 style="color: var(--primary-dark); font-size: 12px; margin-bottom: 20px; text-align: center;">
                    APPROBATIONS
                </h3>
                <div class="signature-grid">
                    <div class="signature-box">
                        <div class="signature-line"></div>
                        <div class="signature-label">Responsable des Achats</div>
                    </div>
                    <div class="signature-box">
                        <div class="signature-line"></div>
                        <div class="signature-label">Date d'Approbation</div>
                    </div>
                </div>
            </div>

            <!-- Pied de page -->
            <div class="footer">
                <div class="footer-info">
                    <strong>Merci pour votre collaboration!</strong><br>
                    {company['name']} - Licence RBQ: {company['rbq']}<br>
                    {company['phone']} | {company['email']}<br>
                    {company['address']}, {company['city']}, {company['province']} {company['postal_code']}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return html