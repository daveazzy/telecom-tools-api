"""RF calculation services"""

import math
from typing import Tuple, Dict


class RFCalculations:
    """Class for radio frequency calculations"""
    
    @staticmethod
    def friis_path_loss(frequency_mhz: float, distance_km: float) -> float:
        """
        Calculate free space path loss using Friis equation.
        FSPL = 20*log10(d) + 20*log10(f) + 32.45
        
        Args:
            frequency_mhz: Frequency in MHz
            distance_km: Distance in kilometers
            
        Returns:
            Path loss in dB
        """
        distance_m = distance_km * 1000
        frequency_ghz = frequency_mhz / 1000
        
        fspl = 20 * math.log10(distance_m) + 20 * math.log10(frequency_ghz) + 92.45
        return fspl
    
    @staticmethod
    def okumura_hata_path_loss(
        frequency_mhz: float,
        distance_km: float,
        tx_height_m: float = 30,
        rx_height_m: float = 1.5,
        environment: str = "urban"
    ) -> float:
        """
        Calculate path loss using Okumura-Hata model for urban propagation.
        Valid for: 150-1500 MHz, 1-20 km, tx height 30-200m, rx height 1-10m
        
        Args:
            frequency_mhz: Frequency in MHz
            distance_km: Distance in kilometers
            tx_height_m: Transmitter height in meters
            rx_height_m: Receiver height in meters
            environment: Environment type (urban, suburban, rural)
            
        Returns:
            Path loss in dB
        """
        # Mobile antenna height correction factor
        if frequency_mhz <= 200:
            a_hr = 8.29 * (math.log10(1.54 * rx_height_m))**2 - 1.1
        else:
            a_hr = 3.2 * (math.log10(11.75 * rx_height_m))**2 - 4.97
        
        # Basic path loss
        L50 = (69.55 + 26.16 * math.log10(frequency_mhz) 
               - 13.82 * math.log10(tx_height_m) 
               - a_hr 
               + (44.9 - 6.55 * math.log10(tx_height_m)) * math.log10(distance_km))
        
        # Environment adjustment
        if environment == "suburban":
            L50 -= 2 * (math.log10(frequency_mhz / 28))**2 + 5.4
        elif environment == "rural":
            L50 -= 4.78 * (math.log10(frequency_mhz))**2 + 18.33 * math.log10(frequency_mhz) + 40.94
        
        return L50
    
    @staticmethod
    def link_budget_analysis(
        tx_power_dbm: float,
        tx_gain_dbi: float,
        rx_gain_dbi: float,
        frequency_mhz: float,
        distance_km: float,
        additional_losses_db: float = 0,
        rx_sensitivity_dbm: float = -100
    ) -> Dict:
        """
        Perform complete link budget analysis.
        
        Args:
            tx_power_dbm: Transmit power in dBm
            tx_gain_dbi: Transmit antenna gain in dBi
            rx_gain_dbi: Receive antenna gain in dBi
            frequency_mhz: Frequency in MHz
            distance_km: Distance in kilometers
            additional_losses_db: Additional losses in dB
            rx_sensitivity_dbm: Receiver sensitivity in dBm
            
        Returns:
            Dictionary with link budget results
        """
        # Calculate path loss
        path_loss = RFCalculations.friis_path_loss(frequency_mhz, distance_km)
        
        # EIRP (Effective Isotropic Radiated Power)
        eirp_dbm = tx_power_dbm + tx_gain_dbi
        
        # Received power
        rx_power_dbm = eirp_dbm + rx_gain_dbi - path_loss - additional_losses_db
        
        # Link margin
        link_margin_db = rx_power_dbm - rx_sensitivity_dbm
        
        return {
            "received_power_dbm": round(rx_power_dbm, 2),
            "path_loss_db": round(path_loss, 2),
            "free_space_loss_db": round(path_loss, 2),
            "eirp_dbm": round(eirp_dbm, 2),
            "total_gain_db": round(tx_gain_dbi + rx_gain_dbi, 2),
            "link_margin_db": round(link_margin_db, 2),
            "is_viable": link_margin_db > 0,
            "fade_margin_db": round(link_margin_db, 2) if link_margin_db > 0 else 0
        }
    
    @staticmethod
    def dbm_to_watts(dbm: float) -> float:
        """
        Convert dBm to Watts.
        
        Args:
            dbm: Power in dBm
            
        Returns:
            Power in Watts
        """
        return 10 ** ((dbm - 30) / 10)
    
    @staticmethod
    def watts_to_dbm(watts: float) -> float:
        """
        Convert Watts to dBm.
        
        Args:
            watts: Power in Watts
            
        Returns:
            Power in dBm
        """
        return 10 * math.log10(watts * 1000)
    
    @staticmethod
    def dbm_to_mw(dbm: float) -> float:
        """
        Convert dBm to milliwatts.
        
        Args:
            dbm: Power in dBm
            
        Returns:
            Power in milliwatts
        """
        return 10 ** (dbm / 10)
    
    @staticmethod
    def mw_to_dbm(mw: float) -> float:
        """
        Convert milliwatts to dBm.
        
        Args:
            mw: Power in milliwatts
            
        Returns:
            Power in dBm
        """
        return 10 * math.log10(mw)
    
    @staticmethod
    def db_to_linear(db: float) -> float:
        """
        Convert dB to linear scale.
        
        Args:
            db: Value in dB
            
        Returns:
            Linear value
        """
        return 10 ** (db / 10)
    
    @staticmethod
    def linear_to_db(linear: float) -> float:
        """
        Convert linear scale to dB.
        
        Args:
            linear: Linear value
            
        Returns:
            Value in dB
        """
        return 10 * math.log10(linear)
    
    @staticmethod
    def wavelength(frequency_hz: float) -> float:
        """
        Calculate wavelength from frequency.
        
        Args:
            frequency_hz: Frequency in Hz
            
        Returns:
            Wavelength in meters
        """
        c = 3e8  # Speed of light in m/s
        return c / frequency_hz
    
    @staticmethod
    def fresnel_zone_radius(
        distance_km: float,
        frequency_mhz: float,
        zone_number: int = 1
    ) -> float:
        """
        Calculate Fresnel zone radius at the midpoint.
        
        Args:
            distance_km: Distance between transmitter and receiver in km
            frequency_mhz: Frequency in MHz
            zone_number: Fresnel zone number (typically 1)
            
        Returns:
            Radius in meters
        """
        distance_m = distance_km * 1000
        wavelength_m = RFCalculations.wavelength(frequency_mhz * 1e6)
        
        # Radius at midpoint
        radius_m = math.sqrt((zone_number * wavelength_m * distance_m) / 4)
        return radius_m
    
    @staticmethod
    def antenna_gain_from_diameter(
        frequency_mhz: float,
        diameter_m: float,
        efficiency: float = 0.6
    ) -> float:
        """
        Calculate antenna gain from diameter (parabolic dish).
        
        Args:
            frequency_mhz: Frequency in MHz
            diameter_m: Antenna diameter in meters
            efficiency: Antenna efficiency (0-1, typically 0.5-0.7)
            
        Returns:
            Gain in dBi
        """
        wavelength_m = RFCalculations.wavelength(frequency_mhz * 1e6)
        gain_linear = efficiency * (math.pi * diameter_m / wavelength_m) ** 2
        gain_dbi = 10 * math.log10(gain_linear)
        return gain_dbi
    
    @staticmethod
    def calculate_distance(
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate (latitude, longitude in degrees)
            lat2, lon2: Second coordinate (latitude, longitude in degrees)
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in km
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    @staticmethod
    def estimate_signal_from_tower(
        distance_km: float,
        tx_power_dbm: float = 43,
        tx_gain_dbi: float = 15,
        rx_gain_dbi: float = 0,
        frequency_mhz: float = 2100,
        tx_height_m: float = 30,
        rx_height_m: float = 1.5
    ) -> float:
        """
        Estimate signal strength at a point from a transmitter using Okumura-Hata.
        Simplified formula for urban/suburban areas.
        
        Args:
            distance_km: Distance to transmitter in km
            tx_power_dbm: Transmit power in dBm (default 43 dBm = 20W for cellular)
            tx_gain_dbi: Transmit antenna gain in dBi
            rx_gain_dbi: Receive antenna gain in dBi (0 for omni)
            frequency_mhz: Frequency in MHz (default 2100 = LTE band 1)
            tx_height_m: Tower height in meters
            rx_height_m: Receiver height in meters (hand-held phone)
            
        Returns:
            Signal strength in dBm
        """
        if distance_km < 0.01:  # avoid log(0)
            return tx_power_dbm
        
        # Okumura-Hata path loss (urban environment)
        path_loss = RFCalculations.okumura_hata_path_loss(
            frequency_mhz=frequency_mhz,
            distance_km=distance_km,
            tx_height_m=tx_height_m,
            rx_height_m=rx_height_m,
            environment="urban"
        )
        
        # Received power = EIRP - Path Loss + RX Gain
        eirp_dbm = tx_power_dbm + tx_gain_dbi
        rx_power_dbm = eirp_dbm - path_loss + rx_gain_dbi
        
        # Clamp to realistic range
        return max(-120, min(0, rx_power_dbm))


# Global instance
rf_calc = RFCalculations()

