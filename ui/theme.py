"""
Paleta de cores e estilos fiéis ao MultDownload 4.2.0 Desktop
"""

class Theme:
    # Cores de Ação (Idênticas ao Desktop)
    RED_ACTION = [0.98, 0.35, 0.35, 1.0]       # #FA5858 (Baixar Vídeo)
    BLUE_ACTION = [0.13, 0.58, 0.95, 1.0]      # #2196F3 (Baixar Áudio)
    GREEN_SUCCESS = [0.18, 0.80, 0.44, 1.0]    # #2ECC71 (Sucesso)
    ORANGE_WARNING = [0.95, 0.61, 0.07, 1.0]   # #F39C12 (Aviso)
    
    # Cores Tema Claro
    LIGHT_BG = [0.96, 0.97, 0.98, 1.0]         # #F5F7FA
    LIGHT_CARD = [1.0, 1.0, 1.0, 1.0]          # #FFFFFF
    LIGHT_TEXT = [0.15, 0.17, 0.20, 1.0]       # #272B33
    LIGHT_SUBTEXT = [0.45, 0.50, 0.55, 1.0]    # #73808C
    LIGHT_BORDER = [0.88, 0.90, 0.92, 1.0]     # #E0E6EB
    LIGHT_INPUT_BG = [0.94, 0.95, 0.96, 1.0]   # #F0F2F5

    # Cores Tema Escuro
    DARK_BG = [0.08, 0.09, 0.11, 1.0]          # #14171C
    DARK_CARD = [0.14, 0.15, 0.18, 1.0]        # #24272E
    DARK_TEXT = [0.95, 0.96, 0.98, 1.0]        # #F2F5FA
    DARK_SUBTEXT = [0.65, 0.68, 0.73, 1.0]     # #A6AEBA
    DARK_BORDER = [0.22, 0.24, 0.28, 1.0]      # #383D47
    DARK_INPUT_BG = [0.18, 0.20, 0.23, 1.0]    # #2E333B

    @classmethod
    def get_bg(cls, is_dark):
        return cls.DARK_BG if is_dark else cls.LIGHT_BG

    @classmethod
    def get_card(cls, is_dark):
        return cls.DARK_CARD if is_dark else cls.LIGHT_CARD

    @classmethod
    def get_text(cls, is_dark):
        return cls.DARK_TEXT if is_dark else cls.LIGHT_TEXT

    @classmethod
    def get_subtext(cls, is_dark):
        return cls.DARK_SUBTEXT if is_dark else cls.LIGHT_SUBTEXT

    @classmethod
    def get_border(cls, is_dark):
        return cls.DARK_BORDER if is_dark else cls.LIGHT_BORDER

    @classmethod
    def get_input_bg(cls, is_dark):
        return cls.DARK_INPUT_BG if is_dark else cls.LIGHT_INPUT_BG
