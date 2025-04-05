# ScheduleApp

To run this app, you will need to have Docker installed. You can build the Docker
image for this app by running this command in the root folder: `docker build -t pyapp .`

Run the app by typing this command: `docker run -d -p 8000:8000 pyapp`

# Tools Used

This app was made using the pyonceperday library (written by myself), pytest, uv, Django, and Docker. 

You can run the tests for this app by installing uv and running `uv sync`. After
the environment has been synced, run `uv run manage.py test` in the root folder. 

# Mockups

A look at the UI mockup can be [found here](https://www.figma.com/design/p31WfgPPtGsUuCPUyF0s7f/Mockup?node-id=0-1&p=f)

# Assumptions

I made several assumptions. The first is that the event would be a maximum of 120 minutes. The second assumption is that event repeat up to 4 weeks. 




