# **Jupyterlite-xblock**
The JupyterLite XBlock is an advanced educational tool designed to seamlessly integrate JupyterLite, a lightweight Jupyter notebook environment, into Open edX. This integration allows both instructors and learners to leverage the powerful features of Jupyter notebooks directly within the Open edX platform. Here are its key features:
- **JupyterLite Integration**: Embeds JupyterLite for interactive Python coding within course content.
- **Configurable Notebook Settings**: Instructors can set the JupyterLite service URL and a default notebook.
- **Notebook Tracking**: Tracks learner interactions with notebooks, saving their progress.
- **Interactive Learning**: Offers real-time coding practice and results visualization.
- **Notebook Storage**: Facilitates saving and retrieval of notebooks within the platform.
- **Completion Tracking**: Configurable to mark notebook interactions as course completion criteria.
- **Studio Interface**: Easily manage JupyterLite settings and notebooks in Open edX Studio.
- **User-Friendly Interface**: Enhanced with custom JavaScript and HTML for an interactive experience.


## **Setup**
### **Install the jupyterlite xblock**
```bash
 pip install jupyterlite-xblock
```
### **Install the jupyterlite plugin**
The plugin is currently not available in tutor public indexes at the moment. To install it you should have access to git repo:
```bash
pip install git+https://github.com/edly-io/tutor-contrib-jupyterlite.git
```
### **Enable the jupyterlite plugin**
```bash
tutor plugins enable jupyterlite
```
### **Build image and launch:**
```bash
tutor images build jupyterlite
tutor [dev|local] launch
```

### **Update Advanced Settings of course**
Update course advanced settings by adding `jupyterlite_xblock` as shown in below image and save changes 

![Update settings image](https://github.com/edly-io/jupyterlite-xblock/blob/master/docs/images/update-settings.png?raw=True)

Now you can access the jupyterlite xblock feature in the advanced component of course unit


#### **Update settings of Jupyter Component**

AI Coach Xblock will be available in Advanced component of course unit now. Add "JupyterLite" xblock in unit and click "Edit" button
Access Edit Settings: Once the XBlock is added, click on the "Edit" button to open the configuration settings.

#### **Set JupyterLite Service URL:**
In the "JupyterLite base URL" field, enter the URL of your JupyterLite service. This URL is where the JupyterLite server is hosted.
Example: http://jupyterlite.yourservice.com/lab/index.html
This setting defines the base URL for the JupyterLite environment that learners will interact with.

#### **Upload Default Notebook:**
You have the option to upload a default .ipynb (IPython Notebook) file. This notebook will be the starting point for learners.
Click on the "Upload .ipynb file" button and select the desired notebook from your computer.
If a notebook is already uploaded, it will display its name. You can replace it by uploading a new file.

#### **Save the Changes:**
 After configuring the settings, click on the "Save" button to apply the changes.


![Configure Jupyter Lite XBlock Image](https://github.com/edly-io/ai-coach-xblock/blob/master/docs/images/upload-jupyter-notebook.png?raw=True)

#### **Add these settings to enable S3 Storage.**
Please make sure your bucket's CORS allow JupyterLite service URL

    XBLOCK_SETTINGS["JupterLiteXBlock"] = {
        "STORAGE_FUNC": "jupyterlitexblock.storage.s3",
        "S3_BUCKET_NAME": "YOUR_BUCKET_NAME_GOES_HERE"
    }

#### Completion Delay Setting: 
Configure the delay for marking an activity as complete. The default is 5 seconds, but it can be adjusted to suit course needs. The setting 'completion_delay_seconds' in XBLOCK_SETTINGS allows you to specify the delay in seconds.
```bash
'completion_delay_seconds': self.xblock_settings.get("COMPLETION_DELAY_SECONDS", 5)
```

### **Publish Content**

Use "Preview" button to preview it or publish your content and use "View Live Version" button to see how it appears on LMS

![View Jupyter Lite XBlock Image](https://github.com/edly-io/ai-coach-xblock/blob/master/docs/images/preview.png?raw=True)
