"""
Paleta de cores e estilos moderna e clean para o MultDownloader
"""

class Theme:
    # Cores de Ação Vibrantes e Modernas
    RED_ACTION = [0.94, 0.27, 0.31, 1.0]       # #EF4444 (Coral Red Moderno)
    BLUE_ACTION = [0.15, 0.50, 0.98, 1.0]      # #2563EB (Electric Blue Moderno)
    GREEN_SUCCESS = [0.13, 0.77, 0.45, 1.0]    # #10B981 (Emerald Green)
    ORANGE_WARNING = [0.96, 0.62, 0.13, 1.0]   # #F59E0B (Amber)
    PURPLE_ACCENT = [0.55, 0.36, 0.96, 1.0]    # #8B5CF6 (Purple)
    
    # Cores Tema Claro (Clean & Airy)
    LIGHT_BG = [0.96, 0.97, 0.98, 1.0]         # #F8FAFC
    LIGHT_CARD = [1.0, 1.0, 1.0, 1.0]          # #FFFFFF
    LIGHT_TEXT = [0.09, 0.11, 0.15, 1.0]       # #0F172A
    LIGHT_SUBTEXT = [0.42, 0.47, 0.55, 1.0]    # #64748B
    LIGHT_BORDER = [0.89, 0.91, 0.94, 1.0]     # #E2E8F0
    LIGHT_INPUT_BG = [0.94, 0.96, 0.98, 1.0]   # #F1F5F9
    LIGHT_BUTTON_BG = [0.92, 0.94, 0.97, 1.0]  # #EAF0F8

    # Cores Tema Escuro (Clean Deep Slate — Elegante e Sem Poluição Visual)
    DARK_BG = [0.07, 0.08, 0.10, 1.0]          # #12151A (Fundo profundo)
    DARK_CARD = [0.11, 0.13, 0.16, 1.0]        # #1C2129 (Card elevado)
    DARK_TEXT = [0.96, 0.97, 0.98, 1.0]        # #F8FAFC (Texto nítido)
    DARK_SUBTEXT = [0.58, 0.62, 0.68, 1.0]     # #949EAD (Subtexto suave)
    DARK_BORDER = [0.18, 0.21, 0.26, 1.0]      # #2E3642 (Borda sutil 1px)
    DARK_INPUT_BG = [0.08, 0.09, 0.12, 1.0]    # #14181F (Campo rebaixado)
    DARK_BUTTON_BG = [0.14, 0.17, 0.22, 1.0]   # #242B38 (Botão de topo)

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

    @classmethod
    def get_button_bg(cls, is_dark):
        return cls.DARK_BUTTON_BG if is_dark else cls.LIGHT_BUTTON_BG

