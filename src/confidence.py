class ConfidenceCalibrator:
    def __init__(self):
        pass

    def calibrate(self, base_confidence, has_evidence=False, low_confidence_media=False, signal_conflict=False):
        conf = float(base_confidence)

        if has_evidence:
            conf += 0.03
        else:
            conf -= 0.02

        if low_confidence_media:
            conf -= 0.05

        if signal_conflict:
            conf -= 0.08

        # Bound between 0.60 and 0.95
        conf = max(0.60, min(0.95, conf))
        return round(conf, 2)
