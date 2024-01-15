from datetime import datetime
    
class Utils:
    def get_current_date() -> dict:
        """
        Récupère la date actuelle et son timestamp

        :return: date actuelle (datetime obj) et timestamp (int)
        :rtype: dict
        """
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return {"date": now, "date_timespamp": timestamp}
        
    
            