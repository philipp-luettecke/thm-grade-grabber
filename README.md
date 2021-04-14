# THM Grade Grabber 
This script is supposed to grab your grades from the THM "Service für Studierende".

## Setup

Before being able to use the script, you will have to install certain programs:

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install --no-install-recommends python3 python3-pip chromium-bsu chromium-driver chromium-chromedriver mosquitto
sudo python3 -m pip install selenium paho.mqtt

```

After this you are able to run the script by executing:

```bash
python3 grab.py
```


## Config.ini
At `[USERDATA]` please provide your THM CAS Credentials.

At `[MQTT]` please provide host and port of your MQTT broker. If you also have a user and password here, provide it as well.
The "topic" is the base-topic, where the mqtt messages will be published to.

At `[GENERAL]` you can provide the interval, in which the script is supposed to check for updates.

## How it works

## Configuration in Home-Assistant

To add the THM Grades to Home Assistant you will have to add two MQTT Sensors as shown below.
For the case, that you changed the base_topic in the config.ini file, you will have to adapt the mqtt topics accordingly.

### Add MQTT Sensors

```yaml
sensor:
  - platform: mqtt
    name: "THM_Grades"
    state_topic: "thm_grabber/sensor"
    unit_of_measurement: ""
    json_attributes_topic: "thm_grabber/grades"

  - platform: mqtt
    name: "THM_Grades_Summary"
    state_topic: "thm_grabber/summary"
    value_template: "{{ value_json.percentage }}"
    unit_of_measurement: "%"
    json_attributes_topic: "thm_grabber/summary"
```
### Available attribtues
| Attribute | Description | 
| --- | --- |
| number | Represents the Module Number (TI5001 etc.) |
| description | Contains the Name of the Module |
| semester | Contains the Semester, the Module was visited |
| grade | Contains the grade of the exam (1,3 etc) |
| percentage | Contains the percentage (93) |
| state | Contains either "bestanden" or "nicht bestanden" |
| credits | Represents the credit points for the module |


### New Grade Notification
There is another topic, where messages are published, once there is a new grade detected, that was not listed before. 
The topic is called `thm_grabber/new_grade`, which will have the new detected grade as json value. 
You can use the mqtt message as a sensor or a trigger for automations.

```yaml
sensor:
  - platform: mqtt
    name: "THM_Grades_New_Grade"
    state_topic: "thm_grabber/new_grade"
    value_template: "{{ value_json.description }}"
    unit_of_measurement: "%"
    json_attributes_topic: "thm_grabber/new_grade"
```

In an automation you can also use the topic `thm_grabber/new_grade` as a trigger. 
You are then able to e.g. send a Notification to your Phone using the data of the MQTT Message like this:
`{{ trigger.payload_json["description"] }}`

```yaml
service: notify.pixel_3
data_template:
  message: >-
    {% set keys = trigger.payload_json.keys() | list %} 
    New Grade {{ trigger.payload_json[keys[0]]['description'] }} - {{ trigger.payload_json[keys[0]]['grade'] }} with {{ trigger.payload_json[keys[0]]['percentage'] }}%
  title: New grade entered at THM
```

### Markdown Card to Display the Grades

Add a new Markdown Card to the Lovelcae UI. Paste the following code to get a full list of the available grades.


```bash
Übersicht:
**Gesamtnote:** {{ state_attr('sensor.thm_grades_summary', 'grade') }} 
**Prozentsatz:** {{ state_attr('sensor.thm_grades_summary', 'percentage') }}%

| Nummer | Beschreibung | Note | Prozent |
| ------ | :----------- | :---: | :----: |
{%- for grade in states.sensor if grade.entity_id.endswith('thm_grades') -%}
  {%- for attr in grade.attributes if not attr.startswith('unit') and not attr.startswith('friendly') -%}
  {%- if state_attr('sensor.thm_grades', attr)["number"].endswith('000') or state_attr('sensor.thm_grades', attr)["number"].endswith('AP') or state_attr('sensor.thm_grades', attr)["number"].endswith('WPF')%}
  | **{{ state_attr('sensor.thm_grades', attr)["number"] }}** |  **{{ state_attr('sensor.thm_grades', attr)["description"] }}** | **{{ state_attr('sensor.thm_grades', attr)["grade"] }}** | **{{ state_attr('sensor.thm_grades', attr)["percentage"] }}** |
  {% else %}
  | {{ state_attr('sensor.thm_grades', attr)["number"] }} | {{ state_attr('sensor.thm_grades', attr)["description"] }} |  {{ state_attr('sensor.thm_grades', attr)["grade"] }} | {{ state_attr('sensor.thm_grades', attr)["percentage"] }} |
  {% endif %}
  {%- endfor -%}
{%- endfor -%}
```

