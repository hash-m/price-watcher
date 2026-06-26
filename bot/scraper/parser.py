
def calculate_percentage(initial,final):
    if initial is None or final is None or initial == 0:
        return 0
    
    return 100 * (1- (final/initial))
    
def format_percentage(percentage):
    if percentage is None:
        return 0.0
    
    if isinstance(percentage, (int, float)):
        return float(percentage)
    
    return float(str(percentage).strip().strip('%'))

def format_price(price):
    if price is None:
        return None
    
    if isinstance(price, (int, float)):
        return float(price)
    
    return round(float(str(price).strip().strip('£')), 2)

def format(raw_info):
    info = dict(raw_info)

    if "FinalPrice" in info:
        info["FinalPrice"] = format_price(info["FinalPrice"])

    if "InitialPrice" in info:
        info["InitialPrice"] = format_price(info["InitialPrice"])

    if "Percentage" in info:
        info["Percentage"] = format_percentage(info["Percentage"])
    elif "InitialPrice" in info and "FinalPrice" in info:
        info["Percentage"] = calculate_percentage(info["InitialPrice"], info["FinalPrice"])

    return info