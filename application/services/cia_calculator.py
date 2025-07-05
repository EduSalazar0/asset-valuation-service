import logging

logger = logging.getLogger(__name__)

class CIACalculatorService:
    """
    Implements the CIA/SCA valuation logic based on heuristics.
    This class automates the "Cuestionario de Valoración CIA" from the project methodology.
    """

    def _get_cia_metrics(self, asset_value: str) -> dict:
        """
        Heuristic-based assignment of CIA metrics.
        In a real system, this could be much more complex, involving regex,
        port scanning results, or other contextual data.
        
        Metrics are on a 0-1 scale as per the methodology document.
        """
        metrics = {
            'confidentiality': [],
            'integrity': [],
            'availability': []
        }
        
        # Heuristic 1: Data sensitivity based on keywords
        if any(kw in asset_value for kw in ["api", "login", "auth", "admin"]):
            metrics['confidentiality'].append(0.9) # High need for C
        else:
            metrics['confidentiality'].append(0.4) # Medium need
            
        # Heuristic 2: Data integrity based on keywords
        if any(kw in asset_value for kw in ["db", "database", "storage", "erp"]):
            metrics['integrity'].append(0.95) # High need for I
        else:
            metrics['integrity'].append(0.5)

        # Heuristic 3: Availability needs
        if any(kw in asset_value for kw in ["www", "api", "app", "store"]):
             metrics['availability'].append(0.9) # High need for A
        else:
             metrics['availability'].append(0.6)

        # Add more placeholder metrics to simulate the questionnaire
        metrics['confidentiality'].append(0.6) # e.g., MFA usage (assumed)
        metrics['integrity'].append(0.7)       # e.g., Hashing usage (assumed)
        metrics['availability'].append(0.8)    # e.g., Backup frequency (assumed)

        return metrics

    def calculate_sca(self, asset_value: str) -> dict:
        """
        Calculates the final SCA score for a given asset.
        Returns a dictionary with all calculated scores.
        """
        logger.info(f"Calculating SCA for asset: {asset_value}")
        
        metrics = self._get_cia_metrics(asset_value)
        
        # Formula: Dim_final = (SUM(mi) / n) * 10
        sca_c = (sum(metrics['confidentiality']) / len(metrics['confidentiality'])) * 10
        sca_i = (sum(metrics['integrity']) / len(metrics['integrity'])) * 10
        sca_d = (sum(metrics['availability']) / len(metrics['availability'])) * 10

        # Special rule: If a regulation applies (simulated), score is maxed.
        # For example, if it handles personal data (e.g., login portal).
        if any(kw in asset_value for kw in ["login", "auth", "user"]):
            logger.info("Regulation rule applied: maxing out Confidentiality score.")
            sca_c = 10.0

        # Formula: SCA = (SCA_C + SCA_I + SCA_D) / 3
        sca_total = (sca_c + sca_i + sca_d) / 3

        result = {
            "sca": round(sca_total, 2),
            "sca_c": round(sca_c, 2),
            "sca_i": round(sca_i, 2),
            "sca_d": round(sca_d, 2),
        }
        logger.info(f"Calculation result for {asset_value}: {result}")
        return result