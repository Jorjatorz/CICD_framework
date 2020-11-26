# Machine Learning CI/CD framework
This personal project aims to create a very simplified Continuous  Integration (CI) and Continuous  Deployment (CD) framework to enable the Data Scientists and Machine Learning Engineers develop their models and automatically train, test and deploy them in a target environment.

This framework is divided into three components (i.e. three Docker containers):
1. **Version Control System (VCS)**: This component is in charge of retrieving the Pull Requests from the desired Github repository and store them into a database. It uses [Singer.io](https://www.singer.io/) to perform this, concretely, the [Github tap](https://github.com/singer-io/tap-github) and the [Postgres target](https://github.com/datamill-co/target-postgres).
2. **Postgres database**: Used to store the Pull Requests information. A default Docker Postgres image is used.
3. **Machine Learning CI/CD module**: This component is in charge of checking if the latest Pull Request (inside the DB) is more recent than the one of the currently deployed model and, if this is the case, clone the repository, train the model, test it and deploy it. This module includes an API to retrieve information about the deployed model and access to its predict method.

![Components Overview](/resources/overview.png)

### Getting Started
1. First, you will need to download and install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) in your machine.

2. Clone the framework [GitHub repository](https://github.com/Jorjatorz/CICD_framework) into your machine. 

3. A static training and test set is required to be downloaded. You can download the example train & test sets from my [drive](https://drive.google.com/drive/folders/1Hu4m6aXiHtojUsqJLLRt6mW9isS09XXt?usp=sharing). Unzip the file (two .csv files) into ```ML/src/data/``` folder.

4. The only required initial configuration is to set your Github access token inside ```VCS/src/config.json```. To create a Github access token, [login to your GitHub account](https://github.com/login), go to the *Personal Access Tokens* settings page, and generate a new token with at least the "repo" scope.

5. The framework is now ready to be used. Execute ```docker-compose up``` (you must be located at the level of the *docker-compose.yaml* file) and wait until the three containers are running.

### Using the framework
The *ML CI/CD* component is now checking the DB to see if a new Pull Request (PR) was accepted (every 15 seconds). When a newer version is detected, it will start the cloning, requirements installation, training, testing and deployment process. By default, the used model's repo is [https://github.com/Jorjatorz/CICD_example_model](https://github.com/Jorjatorz/CICD_example_model), for more information about the model go to the section [ML Model](#ml-model).

In the beginning, if you get an error it is totally normal! The DB is empty and you need to access the *VCS API* endpoint ```127.0.0.1/checkout``` to simulate a Webhook event and create the different DB tables with the PRs data. Once this is done, the *ML CI/CD* component will automatically detect the new PRs and will deploy the model, exposing its API at port 8000 of the *localhost*.

![Model deployed](/resources/deployed.png)

The *VCS* and *ML CI/CD* components expose a REST API at localhost in order to execute different commands. Both APIs comes with documentation that can be displayed with ```localhost:api_port/redoc```
* **VCS API** uses port **80**. To simulate a PR Webhook event from Github, execute ```127.0.0.1/checkout```, the module will fetch all the PRs information from the default repository. (*singer-io/tap-github*)
* **ML CI/CD API** uses port **8000**. Once deployed, you can check the model information by accessing the root ```127.0.0.1:8000/```. To access the predict endpoint, navigate to ```127.0.0.1:8000/predict``` and follow the instructions.

![Root page](/resources/root.png)
![Predict page](/resources/predict.png)
![After prediction page](/resources/predicted.png)

### ML Model
The example model's code can be found at [https://github.com/Jorjatorz/CICD_example_model](https://github.com/Jorjatorz/CICD_example_model). You can introduce your desired model repository by changing the ```GIT_REPO_URL``` of the config file located at ```ML/src/config.py``` **Note:** By default, the model's repository is different than the repository fetched by the VCS component (*singer-io/tap-github*). This is done for an easier simulation of PR events, you can use your own private repository or any other repository with a production-like environment and multiple PR requests. In a real usage of this framework, both the *VCS* repository target and the *ML CI/CD* model's repository should be the same.

For the framework to be able to use a model, the model must contain a ```main.py``` file following the same format of ```model_interface_example.py``` (instead of main.py, you can change the name of the used file in ```ML/src/config.py {MODEL_MODULE}```. This class exposes four methods:
1. **Train**: This method gets the dataset as a parameter and should return a pickle of the trained model using this dataset.
2. **Evaluate**: This method accepts the pickle of a trained model and a test dataset (with the same format as the training dataset) and should return a dictionary with the different evaluation metrics of the model's performance.
3. **Predict**: Given the model's pickle and a list of features, this method must return the prediction of the model made with these features.
4. **Info**: This method must return an arbitrary dictionary containing information about the model (name, type, evaluation metrics, description...).

You should import your model's module and implement the four entry points for your model. See the above-mentioned repository main.py for a working example.

The dataset used for developing this [example model](https://github.com/Jorjatorz/CICD_example_model) has been downloaded from Kaggle's [Web Traffic Time Series Forecasting](https://www.kaggle.com/c/web-traffic-time-series-forecasting) by Google. In this competition, the objective is to create a time series predictor for forecasting the number of visits of different Wikipedia.com pages. The evaluation metric used is [SMAPE](https://en.wikipedia.org/wiki/Symmetric_mean_absolute_percentage_error).

I have chosen this competition as an example because it could be extrapolated to any company seeking to predict its website visits. For the training set, I group all the dataset's pages by date, having the total visits of Wikipedia's webpage per day, from 7/1/2015 to 1/1/2017 (month/day/year format). The test set contains the same information but from 1/1/2017 to 2/1/2017.

Hence, the model that is trained, test and deployed in this example (and that can be accessed through the API) tries to predict the future number of daily views that Wikipedia's webpage will have during the following X days (the feature for the predict method) after the 2/1/2017.

**Note:** The implemented model is a simple Random Forest Regressor of [Scikit-Learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html), which performs fairly good when the full training set is used. For this example, only a small subset of the training data is used for speed and resources consumption, making the model perform badly. You can easily change the number of training instances (i.e. nrows) at ```ML/src/cicd.py - pd.read_csv("../data/train.csv", nrows=5000)``` but keep in mind that your machine will need enough resources to handle the full training dataset.

### Configuration
If you want to customize the example, like changing the Pull Requests repository or use your own model, you can easily change the configuration of the framework.

1. **VCS**: Navigate to ```VCS/src/```. In this folder, you can modify the used source repository inside ```config.json``` or which Github tap's streams are fetched inside ```properties.json``` (for details of the Singer Github tap see its [Readme](https://github.com/singer-io/tap-github)). To change the Postgres Database access configuration, modify ```singer-target-postgres-config.json```.
2. **ML CI/CD module**: The configuration file is located at ```ML/src/config.py```. Inside it, you can modify the Postgres Database access configuration, the name of the Model Stats file, the used model's repository, and other information like the name of the model's entry module (in the example, it is ```main.py```).

### Possible improvements
1. Use [DBT](https://www.getdbt.com/) to transform the Pull Requests stored in the DB and store only "accepted" PRs.
2. Develop more ```/predict``` endpoints for different types of models, like non-temporal regression and classification. This would allow the Data Scientist to just specify the type of its model and the framework would set the suitable endpoint for the model's type.
3. Enable the use of real Webhook events from Github.
4. Develop a service to automatically download the training and test sets specified by the Data Scientist.
5. Enable comparisons between model deployments, displaying variances between the evaluation metrics of the different deployments.
6. (For time series) Display a line graph when a prediction is made, allowing the user to see the actual time series followed by the predicted one.
7. Improve error handling and error messages display.

### Contact
If you have any doubt or problem, do not hesitate to contact me through the provided email in my application.