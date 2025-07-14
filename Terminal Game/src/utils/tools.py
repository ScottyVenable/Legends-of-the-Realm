"""
Tools class for various utility functions including table creation and storytelling.
"""
import os
import time
import shutil
from colorama import Fore, Style
from ..ui.display import clear_console

# Make constants available at module level for imports
try:
    from prettytable import PrettyTable, SINGLE_BORDER, FRAME, DOUBLE_BORDER, ALL, NONE
except ImportError:
    # Create fallback classes and constants
    class FallbackPrettyTable:
        # Define constants as class attributes
        FRAME = "FRAME"
        ALL = "ALL"
        NONE = "NONE"
        
        def __init__(self):
            self.field_names = []
            self.align = "l"
            self.rows = []
            self.min_width = 1
            self.max_width = 80
            self.max_table_width = 80
            self.min_table_width = 10
            self.vrules = None
            self.hrules = None
            self.sortby = None
            self.reversesort = False
            self.title = ""
            
        def add_row(self, row):
            self.rows.append(row)
            
        def set_style(self, style):
            pass
            
        def __str__(self):
            if not self.rows and not self.field_names:
                return ""
            
            # Calculate column widths for better formatting
            all_rows = []
            if self.field_names:
                all_rows.append(self.field_names)
            all_rows.extend(self.rows)
            
            if not all_rows:
                return ""
            
            # Calculate max width for each column
            num_cols = len(all_rows[0]) if all_rows else 0
            col_widths = []
            for col in range(num_cols):
                max_width = 0
                for row in all_rows:
                    if col < len(row):
                        max_width = max(max_width, len(str(row[col])))
                col_widths.append(max(max_width, self.min_width))
            
            # Build the table
            result = ""
            
            # Add title if present
            if self.title:
                result += f"{self.title}\n"
            
            # Add header if field_names exist
            if self.field_names:
                header_row = ""
                for i, name in enumerate(self.field_names):
                    if i < len(col_widths):
                        if self.align == "l":
                            header_row += str(name).ljust(col_widths[i])
                        elif self.align == "r":
                            header_row += str(name).rjust(col_widths[i])
                        else:  # center
                            header_row += str(name).center(col_widths[i])
                    else:
                        header_row += str(name)
                    if i < len(self.field_names) - 1:
                        header_row += " | "
                result += header_row + "\n"
                
                # Add separator line
                separator = ""
                for i, width in enumerate(col_widths):
                    separator += "-" * width
                    if i < len(col_widths) - 1:
                        separator += "-+-"
                result += separator + "\n"
            
            # Add data rows
            for row in self.rows:
                data_row = ""
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        cell_str = str(cell)
                        if self.align == "l":
                            data_row += cell_str.ljust(col_widths[i])
                        elif self.align == "r":
                            data_row += cell_str.rjust(col_widths[i])
                        else:  # center
                            data_row += cell_str.center(col_widths[i])
                    else:
                        data_row += str(cell)
                    if i < len(row) - 1:
                        data_row += " | "
                result += data_row + "\n"
            
            return result.rstrip()
    
    PrettyTable = FallbackPrettyTable
    SINGLE_BORDER = None
    FRAME = "FRAME"
    DOUBLE_BORDER = "DOUBLE_BORDER"
    ALL = "ALL"
    NONE = "NONE"

__all__ = ['Tools', 'PrettyTable', 'SINGLE_BORDER', 'FRAME', 'DOUBLE_BORDER', 'ALL', 'NONE']


class Tools:
    is_music_playing = True
    
    class Values:
        CONSOLE_WIDTH = 0
        DIALOGUE_INTRO_GREETING = 0
        DIALOGUE_NORMAL_GREETING = 1

    @staticmethod
    def get(type_val):
        if type_val == Tools.Values.CONSOLE_WIDTH:
            console_width = shutil.get_terminal_size().columns
            return console_width
        return None
        
    @staticmethod
    def make_table(data, title="", field_names=None, align="l", style=SINGLE_BORDER, title_color=Fore.RESET, vrules=None, hrules=None, sortby=None, reversesort=False, min_width=10, max_width=20):
        """
        Creates a formatted table using PrettyTable.

        Args:
            title (str): The title of the table.
            data (list of lists or dict): The data to display in the table.
            field_names (list, optional): Column names for the table.
            align (str, optional): Alignment for all columns ("l" for left, "r" for right, "c" for center).
            vrules (str, optional): Vertical rules style ("FRAME", "ALL", "NONE").
            hrules (str, optional): Horizontal rules style ("FRAME", "ALL", "NONE").
            sortby (str, optional): Column name to sort the table by.
            reversesort (bool, optional): Reverse the sorting order if True.

        Returns:
            PrettyTable: The formatted table object.
        """
        console_width = Tools.get(Tools.Values.CONSOLE_WIDTH)
        max_width = console_width - 4 if console_width else 80
        table = PrettyTable()

        # Set column names
        if field_names:
            table.field_names = field_names
        elif isinstance(data, dict) and data:
            table.field_names = list(data.keys())
        elif isinstance(data, list) and data and isinstance(data[0], list):
            table.field_names = [str(i) for i in range(len(data[0]))]

        # Add rows
        if isinstance(data, dict):
            table.add_row(list(data.values()))
        else:
            for row in data:
                table.add_row(row)

        # Apply formatting
        if hasattr(table, 'align'):
            table.align = align
        if vrules and hasattr(table, 'vrules'):
            vrules_value = getattr(PrettyTable, vrules, None)
            if vrules_value is not None:
                table.vrules = vrules_value
        if hrules and hasattr(table, 'hrules'):
            hrules_value = getattr(PrettyTable, hrules, None)
            if hrules_value is not None:
                table.hrules = hrules_value
        if sortby and hasattr(table, 'sortby'):
            table.sortby = sortby
            if hasattr(table, 'reversesort'):
                table.reversesort = reversesort
        if title and hasattr(table, 'title'):
            table.title = f"{title_color}{title}{Fore.RESET}"
        if style and hasattr(table, 'set_style'):
            table.set_style(style)
        if max_width and hasattr(table, 'max_width'):
            table.max_width = max_width
        if min_width and hasattr(table, 'min_width'):
            table.min_width = min_width

        return table

    @staticmethod
    def tell_story(story_name, music="music.mp3", wait_speed=5, start_delay=1):
        """Tell an interactive story with music and visual effects."""
        if story_name == "creation":
            from ..audio.audio import Audio
            
            music_path = os.path.join("music", "the_creation.mp3")
            Audio.play_music(music_path)

            clear_console()
            time.sleep(start_delay)
            print(f"""{Fore.LIGHTCYAN_EX}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            
            # Animation frames
            print(f"""{Fore.CYAN}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            
            print(f"""{Fore.LIGHTBLUE_EX}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            time.sleep(2)   

            # Story content
            print(f"{Fore.BLUE}In the vast emptiness before time, a spark ignited...")
            time.sleep(3)

            print(f"{Fore.CYAN}\nTwo beings, {Style.BRIGHT}Lyrian{Style.RESET_ALL} and {Style.BRIGHT}Ozla{Style.RESET_ALL}, awoke to consciousness.")
            time.sleep(wait_speed)

            print("\nThey looked upon the nothingness and, together, dreamed a universe into existence.")
            time.sleep(wait_speed)

            print(f"\nThey shaped the {Fore.YELLOW}radiant realm of Eternum{Style.RESET_ALL}, their divine home, and then breathed life into {Fore.RED}Edoria{Style.RESET_ALL}, a world of swirling molten rock, a canvas for their grand designs.")
            time.sleep(wait_speed)

            print(f"{Fore.GREEN}\nLyrian{Style.RESET_ALL}, captivated by the beauty of creation, declared himself the {Style.BRIGHT}God of Existence{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla{Style.RESET_ALL}, drawn to the mysteries of endings, became the {Style.BRIGHT}God of the End{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print("\nBut their differing perspectives sowed the seeds of discord.")
            time.sleep(wait_speed)

            print(f"\nWithin Eternum, {Fore.MAGENTA}Ozla{Style.RESET_ALL} crafted the {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL}, a realm of darkness and shadow.")
            time.sleep(wait_speed)

            print(f"{Fore.GREEN}\nLyrian{Style.RESET_ALL} sought to banish this encroaching gloom, while {Fore.MAGENTA}Ozla{Style.RESET_ALL} reveled in its growth. Their disagreement fractured their unity, birthing a corrupting force that tainted Eternum's crystalline beauty.")
            time.sleep(wait_speed)

            print(f"{Fore.RED}\nThe Divine Rift{Style.RESET_ALL} tore through their bond. {Fore.GREEN}Lyrian{Style.RESET_ALL} stood as the High Deity, championing light and life. {Fore.MAGENTA}Ozla{Style.RESET_ALL}, embracing the darkness, retreated to the {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL}, her own realm of shadows.")
            time.sleep(wait_speed)

            print(f"\nTheir feud escalated into a cosmic war, the fate of {Fore.YELLOW}Eternum{Style.RESET_ALL} hanging in the balance.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla's{Style.RESET_ALL} monstrous {Fore.RED}Corrupters{Style.RESET_ALL} clashed with {Fore.GREEN}Lyrian's{Style.RESET_ALL} radiant {Fore.CYAN}Eternals{Style.RESET_ALL} in a symphony of destruction. The {Fore.RED}First Battle of the Corruption War{Style.RESET_ALL} painted Eternum with the blood of both sides. Though the Eternals emerged victorious, the cost was immense.")
            time.sleep(wait_speed)

            print("\nThe war raged on, a celestial dance of light and shadow. But in the end, Lyrian's forces prevailed.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla{Style.RESET_ALL} and her {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL} were banished, cast out from Eternum, a testament to the perils of unchecked ambition.")
            time.sleep(wait_speed)

            print("\nIn the wake of conflict, a new dawn arose. {Fore.GREEN}Lyrian{Style.RESET_ALL}, seeking balance and order, brought forth a pantheon of {Style.BRIGHT}Lesser Deities{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print("\nThey were entrusted with the stewardship of the multiverse, guiding mortals and shaping cultures on {Fore.RED}Edoria{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print(f"\nThe echoes of the {Fore.RED}Divine Rift{Style.RESET_ALL} still reverberate through the cosmos. {Fore.RED}Edoria{Style.RESET_ALL} stands as a testament to the eternal struggle between light and darkness, creation and destruction.")
            time.sleep(wait_speed)

            print("\nThe gods may have retreated to their celestial realms, but their influence lingers, shaping the destinies of mortals and reminding them of the delicate balance upon which existence rests.")
            time.sleep(wait_speed + 3)
