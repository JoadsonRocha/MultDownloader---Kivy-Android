import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from ui.theme import Theme
from ui.components import CustomButton, RoundedCard
from core.platform_helper import PlatformHelper

class HistoryItemCard(RoundedCard):
    def __init__(self, item, is_dark=False, on_delete=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 10)
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 110)
        super().__init__(bg_color=Theme.get_card(is_dark), border_color=Theme.get_border(is_dark), **kwargs)

        self.item = item
        self.item_id = item.get("id")
        self.file_path = item.get("file_path", "")

        # Linha Superior: Tipo + Título + Data
        top_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=45)
        
        is_audio = item.get("item_type") == "audio"
        tag_label = Label(
            text="[ÁUDIO]" if is_audio else "[VÍDEO]",
            font_size="10sp",
            bold=True,
            color=Theme.BLUE_ACTION if is_audio else Theme.RED_ACTION,
            size_hint=(None, 1),
            width=50
        )
        top_box.add_widget(tag_label)

        info_box = BoxLayout(orientation='vertical', spacing=2)
        title_lbl = Label(
            text=item.get("title", "Sem título"),
            font_size="13sp",
            bold=True,
            color=Theme.get_text(is_dark),
            halign='left',
            shorten=True,
            shorten_from='right',
            size_hint_y=None,
            height=24
        )
        title_lbl.bind(size=lambda *x: setattr(title_lbl, 'text_size', (title_lbl.width, None)))
        info_box.add_widget(title_lbl)

        time_lbl = Label(
            text=f"{item.get('timestamp', '')} • {os.path.basename(self.file_path)}",
            font_size="11sp",
            color=Theme.get_subtext(is_dark),
            halign='left',
            shorten=True,
            shorten_from='right',
            size_hint_y=None,
            height=18
        )
        time_lbl.bind(size=lambda *x: setattr(time_lbl, 'text_size', (time_lbl.width, None)))
        info_box.add_widget(time_lbl)
        top_box.add_widget(info_box)

        self.add_widget(top_box)

        # Linha Inferior: Botões de Ação
        btn_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=32)

        # Botão Abrir
        btn_open = CustomButton(
            text="Abrir",
            icon="open-in-new",
            font_size="11sp",
            bg_color=Theme.GREEN_SUCCESS,
            size_hint_x=0.38,
            radius=[8, 8, 8, 8]
        )
        btn_open.bind(on_release=lambda x: PlatformHelper.open_file(self.file_path))
        btn_box.add_widget(btn_open)

        # Botão Compartilhar
        btn_share = CustomButton(
            text="Compartilhar",
            icon="share-variant",
            font_size="11sp",
            bg_color=Theme.BLUE_ACTION,
            size_hint_x=0.42,
            radius=[8, 8, 8, 8]
        )
        btn_share.bind(on_release=lambda x: PlatformHelper.share_file(self.file_path))
        btn_box.add_widget(btn_share)

        # Botão Excluir
        btn_del = CustomButton(
            text="Excluir",
            icon="trash-can-outline",
            font_size="11sp",
            bg_color=Theme.RED_ACTION,
            size_hint_x=0.20,
            radius=[8, 8, 8, 8]
        )
        if on_delete:
            btn_del.bind(on_release=lambda x: on_delete(self.item_id))
        btn_box.add_widget(btn_del)

        self.add_widget(btn_box)

class HistoryScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = "history"

        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=[12, 10, 12, 12])

        # Top Bar do Histórico
        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.header_label = Label(
            text="Histórico de Downloads",
            font_size="16sp",
            bold=True,
            color=Theme.get_text(self.app.is_dark),
            halign='left',
            size_hint_x=0.65
        )
        self.header_label.bind(size=lambda *x: setattr(self.header_label, 'text_size', (self.header_label.width, None)))
        top_row.add_widget(self.header_label)

        self.btn_clear = CustomButton(
            text="Limpar",
            icon="trash-can-outline",
            font_size="11sp",
            bg_color=Theme.RED_ACTION,
            size_hint=(None, 1),
            width=90,
            radius=[8, 8, 8, 8]
        )
        self.btn_clear.bind(on_release=lambda x: self.clear_all_history())
        top_row.add_widget(self.btn_clear)
        self.main_layout.add_widget(top_row)

        # Lista com Scroll
        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.items_container = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None
        )
        self.items_container.bind(minimum_height=self.items_container.setter('height'))
        self.scroll.add_widget(self.items_container)
        self.main_layout.add_widget(self.scroll)

        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.refresh_history()

    def refresh_history(self):
        self.items_container.clear_widgets()
        items = self.app.history.get_items()

        if not items:
            empty_lbl = Label(
                text="Nenhum download realizado ainda.\nBaixe vídeos ou músicas para ver seu histórico aqui.",
                font_size="13sp",
                color=Theme.get_subtext(self.app.is_dark),
                halign='center',
                size_hint_y=None,
                height=120
            )
            empty_lbl.bind(size=lambda *x: setattr(empty_lbl, 'text_size', (empty_lbl.width - 40, None)))
            self.items_container.add_widget(empty_lbl)
            return

        for item in items:
            card = HistoryItemCard(
                item=item,
                is_dark=self.app.is_dark,
                on_delete=self.delete_item
            )
            self.items_container.add_widget(card)

    def delete_item(self, item_id):
        self.app.history.remove_item(item_id)
        self.refresh_history()

    def clear_all_history(self):
        self.app.history.clear_history()
        self.refresh_history()

    def update_theme(self, is_dark):
        self.header_label.color = Theme.get_text(is_dark)
        self.refresh_history()
