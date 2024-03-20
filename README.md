# Simple Kivy UI for osm-fieldwork

## Features

- Currently supports `basemapper.py` and `CSVDump.py`, with only minor modifications needed to support the other programs.
-  Generates the form for a program given arguments (which are easily configurable).
- Support for 'required' and 'default' values
- Custom classes for file selection and radio buttons.
- Links to osm_fieldwork and executes the respective function with gathered form args.
- Can compile to android using buildozer (but still some issues linking the osm-fieldwork module on the android build)
- Logs the program output inside an application (good for mobile debugging).
- Argument fields in the form have clickable explanations.

## Considerations
- Textfield type validation (comma seperated, URL) etc, can be added easily
- No ScreenManager yet.


## Some Pictures


![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/eb04c2cf-8755-41ec-abd6-746436f72d5c)
Home

![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/cdbc863a-2709-4c3f-8e1b-5039d356f635)
![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/99ae712d-0472-4716-b81a-f5a98cd36d44)
![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/fb151bf9-bdcf-427a-b990-87f3fd9ad594)
BaseMapper

![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/c2dc9305-eae4-4b43-95cf-53fb08369e9a)
LogStream

![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/874c3c29-c75a-41f7-b4c6-f99df9186a67)
CSVDump


![image](https://github.com/owolabioromidayo/osm-fieldwork-kivy-mock/assets/37741645/16c10d11-dbca-402b-840d-f80391fc8e76)
Argument Description