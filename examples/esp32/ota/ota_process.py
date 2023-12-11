try:
    import micropython_ota
except ImportError:
    import mip
    mip.install("github:olivergregorius/micropython_ota/micropython_ota.py")
except Exception as e:
    print(f"Erro na importação: {e}")
    
    
ota_host = 