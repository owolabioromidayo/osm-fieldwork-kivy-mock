import logging, os

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton


from osm_fieldwork.basemapper import create_basemap_file
from osm_fieldwork.CSVDump import CSVDump



#Could use a better format than this but works for now
form_layout = {
    'CSVDump.py': {
        "form_desc": "Convert CSV from ODK Central to OSM XML",  
        "verbose": {"desc": "verbose output", "type": "CheckBox"},
        "yaml": {"desc": "Alternate YAML file", "type": "FilePicker"},
        "xlsfile": {"desc": "Source XLSFile", "type": "FilePicker"},
        "infile": {"desc": "The input file downloaded from ODK Central", "required": True, "type": "FilePicker"} ,

    },
    "basemapper.py" : {
        "form_desc": "This main function lets this class be run standalone by a bash script.", 
        "verbose": {"desc": "verbose output" , "type": "CheckBox"},
        "boundary": {"desc": "The boundary for the area you want", "type": "FilePicker"},
        "tms": {"desc": "Custom TMS URL", "type": "TextInput", "args": "URL"},
        "xy": {"desc": "The input file downloaded from ODK Central", "required": True, "type": "TextInput"} ,
        "zooms": {"desc": "The Zoom Levels", "default": "12-17", "type": "TextInput"},
        "outfile": {"desc": "Output file name, allowed extensions [.mbtiles/.sqlitedb/.pmtiles]", 
                    "type":"FilePicker"},
        "source": {"desc": "Imagery source", "default":"esri", "type":"RadioButtons", "args": ["esri", "bing", "topo", "google", "oam"], "required": True},

    },
    # 'json2osm.py': {
    #     "form_desc": "",  
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "yaml": {"help": "Alternate YAML file"},
    #     "xlsfile": {"help": "Source XLSFile"},
    #     "infile": {"help": "The input file downloaded from ODK Central", "required": True} ,

    # }, 
    # 'odk2csv.py': {
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "instance": {"help": "The instance file(s) from ODK Collect", "required": True} ,

    # },
    # 'odk2geojson.py' : {
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "instance": {"help": "The instance file(s) from ODK Collect", "required": True} ,
    #     "outfile": {"help": "The output file for JOSM", "default": "tmp.geojson"} ,

    # },
    # 'odk2osm.py' : {
    #     "form_desc": "Convert ODK XML instance file to OSM XML format.",  
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "instance": {"help": "The instance file(s) from ODK Collect", "required": True} ,

    # },
    # 'odk_merge.py' : {
    #     "--verbose": {"help": "verbose output", "action": "store_true"},
    #     "--yaml": {"help": "Alternate YAML file"},
    #     "--xlsfile": {"help": "Source XLSFile"},
    #     "--infile": {"help": "The input file downloaded from ODK Central", "required": True} ,

    # }, 
    # 'odk_client.py': {
    #     "--verbose": {"help": "verbose output", "action": "store_true"},
    #     "--yaml": {"help": "Alternate YAML file"},
    #     "--xlsfile": {"help": "Source XLSFile"},
    #     "--infile": {"help": "The input file downloaded from ODK Central", "required": True} ,

    # }, 
    # 'filter_data.py': {
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "yaml": {"help": "Alternate YAML file"},
    #     "xlsfile": {"help": "Source XLSFile"},
    #     "infile": {"help": "The input file downloaded from ODK Central", "required": True} ,

    # }, 
    # 'osm2favorites.py' : {
    #     "form_desc": "Create an extended feature with Osmand styling.",
    #     "verbose": {"help": "verbose output", "action": "store_true"},
    #     "infile": {"help": "The input file downloaded from ODK Central", "required": True} ,

    # },
}

# make custom dropdown list



class KivyLogHandler(logging.Handler):
    """Print the external function logs inside a Kivy TextInput field."""
    def __init__(self, text_input):
        super(KivyLogHandler, self).__init__()
        self.text_input = text_input

    def emit(self, record):
        log_message = self.format(record)
        self.text_input.text += log_message + '\n'



def csv_dump(verbose: bool, yaml: str, xlsfile: str, infile: str):
    """Copied from main() in CSVDump.py"""

    log = logging.getLogger('csv_dump')

    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if  yaml:
        csvin = CSVDump(yaml)
    else:
        csvin = CSVDump()

    csvin.parseXLS(xlsfile)
    osmoutfile = os.path.basename(infile.replace(".csv", ".osm"))
    csvin.createOSM(osmoutfile)

    jsonoutfile = os.path.basename(infile.replace(".csv", ".geojson"))
    csvin.createGeoJson(jsonoutfile)

    log.debug("Parsing csv files %r" % infile)
    data = csvin.parse(infile)
    # This OSM XML file only has OSM appropriate tags and values
    for entry in data:
        feature = csvin.createEntry(entry)
        # Sometimes bad entries, usually from debugging XForm design, sneak in
        if len(feature) == 0:
            continue
        if len(feature) > 0:
            if "lat" not in feature["attrs"]:
                log.warning("Bad record! %r" % feature)
                continue
            csvin.writeOSM(feature)
            # This GeoJson file has all the data values
            csvin.writeGeoJson(feature)
            # print("TAGS: %r" % feature['tags'])

    csvin.finishOSM()
    csvin.finishGeoJson()
    log.info("Wrote OSM XML file: %r" % osmoutfile)
    log.info("Wrote GeoJson file: %r" % jsonoutfile)


class RadioButtons(BoxLayout):
    """Radio Button group class"""
    def __init__(self, args, **kwargs):
        super(RadioButtons, self).__init__(**kwargs)

        self.args = args
        self.selected = None
        self.build()

    def build(self):
        for choice in self.args:
            radiobutton = ToggleButton(text=f"{choice}", group='options')
            radiobutton.bind(on_press=self.on_radio_button_pressed)
            self.add_widget(radiobutton)

    def on_radio_button_pressed(self, instance):
        self.selected = [widget for widget in instance.parent.children if isinstance(widget, ToggleButton) and widget.state == 'down']
        if self.selected:
            print("Selected option:", self.selected_option[0].text)

    def get_choice(self):
        if self.selected:
            return self.selected[0].text
        return None 
        

### FILE PICKER #########
class LoadDialog(BoxLayout):
    """File Picker Dialog"""
    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)

        self.path = None
        self.orientation = 'vertical'

        filechooser = FileChooserListView()
        self.add_widget(filechooser)

        button_layout = BoxLayout(size_hint_y=None, height=30)
        
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_release=self.cancel)
        button_layout.add_widget(cancel_button)

        load_button = Button(text='Load')
        load_button.bind(on_release=lambda instance: self.load(filechooser.path, filechooser.selection))
        button_layout.add_widget(load_button)

        self.add_widget(button_layout)


    def load(self, path, filename):
        self.path = filename


    def cancel(self, *args):
        # Destroy the LoadDialog
        # parent = self.parent
        # parent.remove_widget(self)
        # self.popup_handle.dismiss()
        self.parent.remove_widget(self) #doesnt work well for now

class FilePickerButton(Button):
    def __init__(self, **kwargs):
        super(FilePickerButton, self).__init__(**kwargs)
        self.load_dialog = LoadDialog()
        
    def on_press(self):
        self.popup = Popup(title="Choose File", content=self.load_dialog, size_hint=(None, None), size=(400, 400))
        self.popup.open()

    def get_path(self):
        if self.load_dialog.path:
            return self.load_dialog.path[0]
        return None

############

class DescriptionPopup(Popup):
    def __init__(self, title, desc, **kwargs):
        super(DescriptionPopup, self).__init__(**kwargs)
        self.title = title
        self.content = Label(text=desc)
        self.size_hint = (None, None)
        self.size = (400, 100) 

class ArgumentForm(GridLayout):
    """Generates form from dict specifications"""
    def __init__(self, program, args, **kwargs):
        super(ArgumentForm, self).__init__(**kwargs)
        self.cols = 2
        self.program = program
        self.args = args
        self.form_data = {k: None for k in args}
        self.form_items = {k: None for k in args}
        self.build()
        


    def build(self):
        # Work on better UI at this level
        for arg, details in self.args.items():
            if arg == "form_desc":
                continue

            label_text = arg + ":"
            label = Label(text=label_text)
            self.add_widget(label)
            label.bind(on_touch_down=lambda instance, touch, title=arg, desc=details['desc'] : self.show_description_popup(instance, touch, title, desc))
            
            if 'type' in details:
            
                if details['type'] == "FilePicker": 
            
                    file_picker_button = FilePickerButton(text="Choose File")
                    self.add_widget(file_picker_button)
                    self.form_items[arg] = file_picker_button

                elif details['type'] == "CheckBox":
                    checkbox = CheckBox()
                    self.add_widget(checkbox)
                    self.form_items[arg] = checkbox

                elif details['type'] == "TextInput":
                    text_input = TextInput()
                    self.add_widget(text_input)
                    self.form_items[arg] = text_input

                elif details['type'] == 'RadioButtons':
                    radio = RadioButtons(details['args'], orientation='horizontal')
                    self.add_widget(radio)
                    self.form_items[arg] = radio 

                
                else:
                    continue #no support yet

        submit_button = Button(text="Submit", size_hint_x=None)
        submit_button.bind(on_press=self.submit_form)
        self.add_widget(submit_button)


    def show_description_popup(self, instance, touch, title, desc):
        if instance.collide_point(*touch.pos):
            popup = DescriptionPopup(title, desc)
            popup.open()

    def submit_form(self, instance):
        for arg, item in self.form_items.items():
            if isinstance(item, TextInput):
                self.form_data[arg] = item.text.strip()
            elif isinstance(item, CheckBox):
                self.form_data[arg] = item.active
            elif isinstance(item, FilePickerButton):
                self.form_data[arg] = item.get_path()
            elif isinstance(item, RadioButtons):
                self.form_data[arg] = item.get_choice()

            #some other validation can be done here, i.e. string regexing

            #handle defaults
            if self.form_data[arg] in ['', None] and 'default' in self.args[arg]:
                self.form_data[arg] = self.args[arg]['default']

            #check required
            if ('required' in self.args[arg] ) and (self.args[arg]['required'] is True) and (self.form_data[arg] in ['', None]):
                popup = Popup(title='Warning', content=Label(text='Form incomplete!'), auto_dismiss=False)
                popup.open()

                #need to write a ScreenManager  to have support for returning to previous page
                return
                
        # DEBUG VIEW form data
        print("Form Data:", self.form_data)


        execs = {
            "basemapper.py": create_basemap_file,
            "CSVDump.py": csv_dump
        }

        del self.form_data['form_desc']

        #logging view setup
        text_input = TextInput(multiline=True)

        log_handler = KivyLogHandler(text_input)
        log_handler.setLevel(logging.DEBUG)
        logging.root.addHandler(log_handler)
        logging.root.setLevel(logging.DEBUG)

        self.popup = Popup(title="Log Stream", content=text_input, size_hint=(None, None), size=(400, 400))
        self.popup.open() #works but only after the program has finished executing

        # if self.program == "basemapper.py":
            #boundary bytesIO has not been merged yet.

        try:
            execs[self.program](**self.form_data)
        except Exception as e:
            print(type(e).__name__, str(e), e.args)
            
            #can create a popup here

        
        #maybe also a popup for when the program suceeds

            
        # elif self.program == "CSVDump.py":
        #     csv_dump(verbose=self.form_data['verbose'], 
        #              yaml=self.form_data['yaml'], xlsfile=self.form_data['xlsfile'], infile=self.form_data['infile'] )

class MyApp(App):
    def build(self):

        layout = BoxLayout(orientation='vertical', padding=10)
        
        # List of buttons
        button_text = ['CSVDump.py', 'basemapper.py', 'json2osm.py',
                       'odk2csv.py', 'odk2geojson.py', 'odk2osm.py', 'odk_merge.py', 
                       'odk_client.py', 'filter_data.py', 'osm2favorites.py']

        for idx , text in enumerate(button_text):
            button = Button(text=f"{text}")
            button.bind(on_press=lambda instance , text=text : self.create_form(instance, text))
            layout.add_widget(button)

        return layout
    

    def create_form(self, instance, text):
        """Create form for a specific program on button click""" 
        custom_form = ArgumentForm(text, form_layout[text])
        popup = Popup(title=form_layout[text]['form_desc'], content=custom_form)
        popup.open()


if __name__ == "__main__":
    MyApp().run()