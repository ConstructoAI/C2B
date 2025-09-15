"""
Template HTML moderne et professionnel pour les bons de commande
Design similaire aux soumissions avec effets visuels améliorés
"""

def generate_modern_html(data, company):
    """Génère le HTML du bon de commande avec un design moderne et professionnel"""

    # Créer le tableau des items avec un design amélioré
    items_html = ""
    for i, item in enumerate(data['items'], 1):
        # Alterner les couleurs de fond pour une meilleure lisibilité
        row_class = 'row-even' if i % 2 == 0 else 'row-odd'
        items_html += f"""
        <tr class="{row_class}">
            <td class="item-number">{i}</td>
            <td class="item-description">
                <div class="item-title">{item['description']}</div>
                {f'<div class="item-details">{item["details"]}</div>' if item.get('details') else ''}
            </td>
            <td class="item-qty">{item['quantite']}</td>
            <td class="item-unit">{item['unite']}</td>
            <td class="item-price">{item['prix_unitaire']:,.2f} $</td>
            <td class="item-total">{item['total']:,.2f} $</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bon de Commande {data['numero']}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }}

            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                animation: slideIn 0.5s ease-out;
            }}

            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}

            /* En-tête avec gradient et effet moderne */
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
                background-size: 20px 20px;
                animation: moveGrid 20s linear infinite;
            }}

            @keyframes moveGrid {{
                0% {{ transform: translate(0, 0); }}
                100% {{ transform: translate(20px, 20px); }}
            }}

            .header-content {{
                position: relative;
                z-index: 1;
            }}

            .header h1 {{
                font-size: 36px;
                font-weight: 700;
                margin-bottom: 15px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                letter-spacing: 2px;
            }}

            .header .numero {{
                font-size: 24px;
                font-weight: 500;
                padding: 10px 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 50px;
                display: inline-block;
                backdrop-filter: blur(10px);
            }}

            .header .date {{
                margin-top: 15px;
                font-size: 16px;
                opacity: 0.95;
            }}

            /* Badges de statut */
            .status-badge {{
                position: absolute;
                top: 40px;
                right: 40px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                backdrop-filter: blur(10px);
            }}

            /* Sections avec design card moderne */
            .section {{
                padding: 30px 40px;
                border-bottom: 1px solid #f1f5f9;
                position: relative;
            }}

            .section::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 40px;
                right: 40px;
                height: 1px;
                background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
            }}

            .section-title {{
                font-size: 14px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
                position: relative;
                padding-left: 15px;
            }}

            .section-title::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 4px;
                height: 20px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 2px;
            }}

            /* Grid d'informations amélioré */
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}

            .info-item {{
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 12px;
                background: #f8fafc;
                border-radius: 10px;
                transition: all 0.3s ease;
            }}

            .info-item:hover {{
                background: #f1f5f9;
                transform: translateX(5px);
            }}

            .info-icon {{
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 20px;
                flex-shrink: 0;
            }}

            .info-content {{
                flex: 1;
            }}

            .info-label {{
                font-size: 12px;
                font-weight: 500;
                color: #64748b;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .info-value {{
                font-size: 15px;
                color: #1e293b;
                font-weight: 600;
            }}

            /* Tableau moderne avec effets */
            .table-container {{
                padding: 0;
                overflow: visible;
            }}

            table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }}

            thead {{
                background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            }}

            th {{
                padding: 16px;
                text-align: left;
                font-weight: 700;
                font-size: 12px;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 2px solid #e2e8f0;
                position: relative;
            }}

            th:first-child {{
                border-radius: 10px 0 0 0;
            }}

            th:last-child {{
                border-radius: 0 10px 0 0;
                text-align: right;
            }}

            tbody tr {{
                transition: all 0.3s ease;
                position: relative;
            }}

            tbody tr:hover {{
                background: #f8fafc;
                transform: scale(1.01);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}

            .row-even {{
                background: #fafbfc;
            }}

            td {{
                padding: 16px;
                border-bottom: 1px solid #f1f5f9;
                color: #334155;
            }}

            .item-number {{
                text-align: center;
                font-weight: 700;
                color: #667eea;
                font-size: 16px;
            }}

            .item-description {{
                max-width: 400px;
            }}

            .item-title {{
                font-weight: 600;
                color: #1e293b;
                font-size: 15px;
                margin-bottom: 4px;
            }}

            .item-details {{
                font-size: 13px;
                color: #64748b;
                line-height: 1.5;
            }}

            .item-qty, .item-unit {{
                text-align: center;
                font-weight: 500;
            }}

            .item-price {{
                text-align: right;
                font-weight: 500;
                color: #475569;
            }}

            .item-total {{
                text-align: right;
                font-weight: 700;
                color: #667eea;
                font-size: 16px;
            }}

            /* Section des totaux avec design moderne */
            .totals {{
                background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                padding: 30px 40px;
            }}

            .totals-container {{
                max-width: 400px;
                margin-left: auto;
            }}

            .total-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 20px;
                margin-bottom: 8px;
                background: white;
                border-radius: 10px;
                transition: all 0.3s ease;
            }}

            .total-row:hover {{
                transform: translateX(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}

            .total-label {{
                font-weight: 500;
                color: #64748b;
                font-size: 14px;
            }}

            .total-value {{
                font-weight: 600;
                color: #334155;
                font-size: 16px;
            }}

            .grand-total {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 16px 24px;
                margin-top: 16px;
                transform: scale(1.02);
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            }}

            .grand-total .total-label {{
                color: white;
                font-size: 16px;
                font-weight: 600;
            }}

            .grand-total .total-value {{
                color: white;
                font-size: 24px;
                font-weight: 700;
            }}

            /* Signatures */
            .signatures {{
                padding: 40px;
                background: #fafbfc;
            }}

            .signature-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 40px;
                margin-top: 30px;
            }}

            .signature-box {{
                text-align: center;
            }}

            .signature-line {{
                border-top: 2px solid #cbd5e1;
                margin: 40px 0 10px;
                position: relative;
            }}

            .signature-label {{
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 500;
            }}

            /* Pied de page élégant */
            .footer {{
                background: linear-gradient(135deg, #1e293b, #334155);
                color: white;
                padding: 30px 40px;
                text-align: center;
            }}

            .footer-content {{
                opacity: 0.95;
            }}

            .footer-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
            }}

            .company-info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.2);
            }}

            .company-info-item {{
                font-size: 13px;
                opacity: 0.9;
            }}

            .company-info-label {{
                font-weight: 600;
                margin-bottom: 4px;
            }}

            /* Impression */
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                .container {{
                    box-shadow: none;
                    border-radius: 0;
                }}
                .header::before {{
                    display: none;
                }}
            }}

            /* Responsive */
            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 28px;
                }}
                .section {{
                    padding: 20px;
                }}
                .info-grid {{
                    grid-template-columns: 1fr;
                }}
                table {{
                    font-size: 14px;
                }}
                td, th {{
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- En-tête moderne avec effet -->
            <div class="header">
                <div class="status-badge">📋 BON DE COMMANDE</div>
                <div class="header-content">
                    <h1>BON DE COMMANDE</h1>
                    <div class="numero">{data['numero']}</div>
                    <div class="date">📅 {data['date']}</div>
                </div>
            </div>

            <!-- Informations de l'entreprise émettrice -->
            <div class="section">
                <div class="section-title">Informations de l'Émetteur</div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-icon">🏢</div>
                        <div class="info-content">
                            <div class="info-label">Entreprise</div>
                            <div class="info-value">{company['name']}</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">📍</div>
                        <div class="info-content">
                            <div class="info-label">Adresse</div>
                            <div class="info-value">{company['address']}, {company['city']}</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">📞</div>
                        <div class="info-content">
                            <div class="info-label">Téléphone</div>
                            <div class="info-value">{company['phone']}</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">✉️</div>
                        <div class="info-content">
                            <div class="info-label">Courriel</div>
                            <div class="info-value">{company['email']}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Informations du fournisseur -->
            <div class="section">
                <div class="section-title">Fournisseur</div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-icon">🏭</div>
                        <div class="info-content">
                            <div class="info-label">Nom du Fournisseur</div>
                            <div class="info-value">{data['fournisseur']['nom']}</div>
                        </div>
                    </div>
                    {f'''<div class="info-item">
                        <div class="info-icon">👤</div>
                        <div class="info-content">
                            <div class="info-label">Personne Contact</div>
                            <div class="info-value">{data['fournisseur']['contact']}</div>
                        </div>
                    </div>''' if data['fournisseur'].get('contact') else ''}
                    {f'''<div class="info-item">
                        <div class="info-icon">📱</div>
                        <div class="info-content">
                            <div class="info-label">Téléphone</div>
                            <div class="info-value">{data['fournisseur']['telephone']}</div>
                        </div>
                    </div>''' if data['fournisseur'].get('telephone') else ''}
                    {f'''<div class="info-item">
                        <div class="info-icon">📧</div>
                        <div class="info-content">
                            <div class="info-label">Courriel</div>
                            <div class="info-value">{data['fournisseur']['email']}</div>
                        </div>
                    </div>''' if data['fournisseur'].get('email') else ''}
                </div>
            </div>

            <!-- Informations du projet -->
            <div class="section">
                <div class="section-title">Détails du Projet</div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-icon">👥</div>
                        <div class="info-content">
                            <div class="info-label">Client</div>
                            <div class="info-value">{data['client']['nom']}</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">🏗️</div>
                        <div class="info-content">
                            <div class="info-label">Nom du Projet</div>
                            <div class="info-value">{data['projet']['nom']}</div>
                        </div>
                    </div>
                    {f'''<div class="info-item">
                        <div class="info-icon">📌</div>
                        <div class="info-content">
                            <div class="info-label">Adresse du Projet</div>
                            <div class="info-value">{data['projet']['adresse']}</div>
                        </div>
                    </div>''' if data['projet'].get('adresse') else ''}
                    {f'''<div class="info-item">
                        <div class="info-icon">🔗</div>
                        <div class="info-content">
                            <div class="info-label">Référence Soumission</div>
                            <div class="info-value">{data['projet']['ref_soumission']}</div>
                        </div>
                    </div>''' if data['projet'].get('ref_soumission') else ''}
                </div>
            </div>

            <!-- Tableau des articles commandés -->
            <div class="section table-container">
                <div class="section-title">Articles Commandés</div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%; text-align: center;">#</th>
                            <th style="width: 45%;">Description</th>
                            <th style="width: 10%; text-align: center;">Quantité</th>
                            <th style="width: 10%; text-align: center;">Unité</th>
                            <th style="width: 15%; text-align: right;">Prix Unitaire</th>
                            <th style="width: 15%; text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
            </div>

            <!-- Section des totaux -->
            <div class="totals">
                <div class="totals-container">
                    <div class="total-row">
                        <span class="total-label">Sous-total</span>
                        <span class="total-value">{data['totaux']['sous_total']:,.2f} $</span>
                    </div>
                    <div class="total-row">
                        <span class="total-label">TPS (5%)</span>
                        <span class="total-value">{data['totaux']['tps']:,.2f} $</span>
                    </div>
                    <div class="total-row">
                        <span class="total-label">TVQ (9.975%)</span>
                        <span class="total-value">{data['totaux']['tvq']:,.2f} $</span>
                    </div>
                    <div class="total-row grand-total">
                        <span class="total-label">MONTANT TOTAL</span>
                        <span class="total-value">{data['totaux']['total']:,.2f} $</span>
                    </div>
                </div>
            </div>

            <!-- Zone de signatures -->
            <div class="signatures">
                <div class="section-title">Approbations</div>
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

            <!-- Pied de page moderne -->
            <div class="footer">
                <div class="footer-content">
                    <div class="footer-title">✨ Merci pour votre collaboration!</div>
                    <div class="company-info">
                        <div class="company-info-item">
                            <div class="company-info-label">{company['name']}</div>
                            <div>{company['phone']} | {company['email']}</div>
                        </div>
                        <div class="company-info-item">
                            <div class="company-info-label">Numéros d'Entreprise</div>
                            <div>RBQ: {company['rbq']} | NEQ: {company['neq']}</div>
                        </div>
                        <div class="company-info-item">
                            <div class="company-info-label">Taxes</div>
                            <div>TPS: {company['tps']} | TVQ: {company['tvq']}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return html