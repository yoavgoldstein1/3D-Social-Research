# 3DSR - Analysis of Social Interaction Using Computer Vision #

![](/Resources/3D_Social_Research_Figure3_colorblind.gif)
![](/Resources/Skeleton.png)
![](/Resources/Goldstein_etal_figure7.jpg)


Video data offer important insights into social processes because they enable direct observation of real-life social interaction. “3D Social Research” (3DSR) uses Computer Vision (CV) and 3D camera footage to study kinesics and proxemics, two core elements of social interaction. 3DSR is especially useful for analyzing physical distance, movement in space, and movement rate. For a fuller explanation of 3DSR, its role in research on social interaction, and a discussion of its capabilities and limitations, see Goldstein, Legewie, and Shiffer-Sebba, 2022.

Below are instructions for using 3DSR on newly collected `.bag` files and for re-creating the findings in Goldstein, Legewie, and Shiffer-Sebba, 2022. The approach can be used on any 3D footage captured in `.bag` files.[^bag] The pipeline involves two main tasks: processing 3D `.bag` RGB-D video files into analyzable `.csv` files,[^two-humans] and applying the analysis procedures from Goldstein, Legewie, and Shiffer-Sebba (2022) to analyzable `.csv` files. The full pipeline takes us around an hour to run, but timing depends on many factors. The processing of `.bag` video files requires Graphical Processing Units (GPUs). If you do not have GPUs on your local machine and would like to process new videos, you will need to use a computing cluster available through your organization, or a cloud computing service such as Google Cloud Platform (GCP). If you do not require processing new videos and are only interested in either analyzing your own `.csv` files (i.e., pre-processed `.bag` files) or analyzing the `.csv` files used in Goldstein, Legewie, and Shiffer-Sebba, 2022, please jump to [Analyzing .csv Files](#analyzing-csv-files). All instructions assume a MacOS/ Linux operating system (sorry).

[^bag]: `.bag` files are a common format for 3D videos. We used [Intel Realsense cameras](https://www.intel.com/content/www/us/en/architecture-and-technology/realsense-overview.html), which record using the necessary format. While these cameras are still available on the consumer market as of October 2022, unfortunately they are being discontinued and may not be available for purchase in the future.
[^two-humans]: Currently 3DSR only supports `.bag` files of videos capturing at least two humans.

## Contents:
- [3DSR - Analysis of Social Interaction Using Computer Vision](#3dsr---analysis-of-social-interaction-using-computer-vision)
  - [Contents:](#contents)
  - [Intro to Processing .bag Files](#intro-to-processing-bag-files)
    - [Setup Processing Using GCP[^sensitive]](#setup-processing-using-gcpsensitive)
    - [Setup Processing Locally](#setup-processing-locally)
    - [Process Video Files](#process-video-files)
  - [Analyzing .csv Files](#analyzing-csv-files)
    - [Analyzing .csv Files on GCP](#analyzing-csv-files-on-gcp)
  - [Reference](#reference)
  - [Contact us](#contact-us)


## Intro to Processing .bag Files ##
In order to process `.bag` files into analyzable `.csv` files Graphical Processing Units (GPUs) are necessary. If you do not have GPU on your local machine, you will need to use a cloud-based service. We cannot guarantee that the repository will work seamlessly in every environment. However, if you have access to Google Cloud Platform (GCP), we provide the recipe that worked for us under [Setup Processing Using GCP](#setup-processing-using-gcp). If you have GPU on your local machine, see [Setup Processing Locally](#setup-processing-locally).

### Setup Processing Using GCP[^sensitive] ###
1. Open `Cloud Console` in the browser.
2. Search for `Vertex AI`, navigate to `Workbench`
3. Click on `New Notebook` => `TensorFlow Enterprise` => `TensorFlow Enterprise 2.10` => `With 1 NVIDIA Tesla T4`
4. Check `Install NVIDIA GPU driver automatically for me`
5. Click `Create`
6. A GPU machine will spin up for you. This may take a few minutes.
7. Click the blue `OPEN JUPYTERLAB` button once available
8. Follow step 1 under [Setup Processing Locally](#setup-processing-locally) below (skip steps 2-3, GCP pre-installed these features) and then continue to [Process Video Files](#process-video-files).
9. To deactivate the machine, go back to the browser menu where you first created it, check the box to the left of the machine name, click the blue "STOP" icon at the top of the window, followed (once the machine has stopped) by the "DELETE" icon.

[^sensitive]: Please be cautious about uploading potentially sensitive (video) data onto cloud services.

### Setup Processing Locally ###
Run the steps below in a MacOS/ Linux Terminal session:

1. Clone the repository, navigate to the 3DSR folder, and create relevant directories (each line is a new command). The git command will ask for your github username and token:
    ```
    git clone https://github.com/yoavgoldstein1/3DSR
    cd 3DSR
    mkdir Inputs
    mkdir Outputs
    ```
2. If you do not have [virtualenv](https://virtualenv.pypa.io/en/latest/) installed, install and initialize it using the following commands:
    ```
    pip install virtualenv 
    virtualenv venv
    ```
    Virtualenv allows creating a self-contained python virtual environment to install the necessary packages.

3. Enter the virtual environment and install the requirements (listed in requirements.txt) using:
    ```
    source venv/bin/activate 
    pip install -r requirements.txt 
    ```
    (Don't worry if this throws a couple of errors)

You are now ready to process video files!

### Process Video Files ###
After setting up your local or remote machine, execute the following:
1. Open `3DSR_Install.ipynb` and run all cells (in GPC you can simply select "Run All Cells" from the "Run" menu at the top) - this notebook installs the video processing dependencies, including:
    - OpenCV python library
    - RealSense SDK python libraries
    - OpenPose binary build. We use a specific branch of the repository that can be found [here](https://github.com/soulslicer/STAF/tree/staf) paired with the `BODY_21A` model.[^body21]
    - Other libraries and os dependencies

[^body21]: The specific `BODY_21A` model we used is unfortunately no longer supported, which may challenge the use of this `3DSR` repository in the future. However, newer more sophisticated models have become available and we hope to either update this repository or create new `3DSR` implementations in the future.

2. Copy the `.bag` file you would like to process into the `/Inputs` directory you created earlier.

3. Open `3DSR_ProcessVideos.ipynb` and replace the paths inside the first cell of the notebook with paths of the `.bag` file you copied into `/Inputs`. Then run all cells of the notebook.

Once done, the `/Outputs` folder should contain your processed `.csv` (the one with the "_1" at the end is the complete one). Download it onto your local machine and follow the next steps to analyze it using the procedures from Goldstein, Legewie, and Shiffer-Sebba (2022), or apply your own analyses.


## Analyzing .csv Files ##
The analyses below assume R is installed. The latest R release can be found on [CRAN](https://cran.r-project.org/bin/macosx/). Again, we cannot guarantee that the repository will work seamlessly in every environment. Below the instructions to analyze `.csv` files on your local machine, we provide a recipe that worked for us on GCP - [analyzing .csv files on GCP](#analyzing-csv-files-on-gcp)

1. Follow step 1 from [Setup Processing Locally](#setup-processing-locally) if you have not already done so.
2. Install [Rust and Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html) to facilitate gif rendering with:
    ```
    curl https://sh.rustup.rs -sSf | sh
    ```
    (Then punch in '1' to proceed with download)

If you are only interested in running the analyses presented in Goldstein, Legewie, and Shiffer-Sebba (2022) on pre-processed `.csv` files, you have two options:

3a. Using Terminal, enter the command:
    ```
    python 3DSR_Run.py --sampled "CSVs/Sampled" --scripted "CSVs/Scripted"
    ```

3b. Using Jupyter notebooks:
    Open and run `3DSR_Notebook.ipynb`

If you would also like to analyze a newly processed `.bag`, now in `.csv` format:

4. Copy the .csv you downloaded at the end of [Process Video Files](#process-video-files) into the `/CSVs/Sampled` folder.

5. Open `3DSR_Notebook.ipynb` and add the path to your `.csv` into the Sampled list in the first cell (immitate the commas and brackets the way they are used for the existing list items). Then run all cells of the notebook.

(Output figures will materialize inside the ``/Outputs`` folder)

### Analyzing .csv Files on GCP ###
1. Open `Cloud Console` in the browser.
2. Search for `Vertex AI`, navigate to `Workbench`
3. Click on `New Notebook` => `R 4.1`
4. Click `Create`
6. An R-enabled machine will spin up for you
7. Click the blue `OPEN JUPYTERLAB` button once available
8. Open Terminal window
9. Follow steps 1,2, and any other desired steps from [Analyzing .csv Files](#analyzing-csv-files) above [^xml]
10. To deactivate the machine, go back to the browser menu where you first created it, check the box to the left of the machine name, click the blue "STOP" icon at the top of the window, followed (once the machine has stopped) by the "DELETE" icon.

[^xml]: In our implementation, xml2 (a dependency of tidyverse) had an issue on GCP, which we resolved following https://www.brodrigues.co/blog/2019-05-18-xml2/. To resolve the issue we opened a file on Terminal using `sudo nano /usr/lib/R/etc/ldpaths`, added two lines to the end of the file: `LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/conda/lib/` and `export LD_LIBRARY_PATH`, and then saved the file.

## Reference ##

Yoav Goldstein, Nicolas M. Legewie, and Doron Shiffer-Sebba. "3D Social Research: Analysis of Social Interaction Using Computer Vision". *Sociological Methods and Research*.

R Packages Used:
- Auguie, Baptiste (2017). gridExtra: Miscellaneous Functions for "Grid" Graphics. R package version 2.3. https://CRAN.R-project.org/package=gridExtra
- Dowle, Matt, and Arun Srinivasan (2021). data.table: Extension of `data.frame`. R package version 1.14.2. https://CRAN.R-project.org/package=data.table
- Hester, Jim, and Jennifer Bryan (2022). glue: Interpreted String Literals. R package version 1.6.2. https://CRAN.R-project.org/package=glue
- Lin Pedersen, Thomas (2020). patchwork: The Composer of Plots. R package version 1.1.1. https://CRAN.R-project.org/package=patchwork
- Lin Pedersen, Thomas, and David Robinson (2020). gganimate: A Grammar of Animated Graphics. R package version 1.0.7. https://CRAN.R-project.org/package=gganimate
- Lüdecke, D (2021). _sjPlot: Data Visualization for Statistics in Social Science_. R package version 2.8.10. https://CRAN.R-project.org/package=sjPlot
- Ooms, Jeroen (2022). gifski: Highest Quality GIF Encoder. R package version 1.6.6-1. https://CRAN.R-project.org/package=gifski
- R Core Team (2021). R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria. https://www.R-project.org/.
- Tierney, Nicholas, Di Cook, Miles McBain and Colin Fay (2021). naniar: Data Structures, Summaries, and Visualisations for Missing Data. R package version 0.6.1. https://CRAN.R-project.org/package=naniar
- Vaughan, Davis (2021). slider: Sliding Window Functions. R package version 0.2.2. https://CRAN.R-project.org/package=slider
- Wickham, H. ggplot2: Elegant Graphics for Data Analysis. Springer-Verlag New York, 2016. https://ggplot2.tidyverse.org
- Wickham et al., (2019). Welcome to the tidyverse. Journal of Open Source Software, 4(43), 1686. https://doi.org/10.21105/joss.01686
- Zeileis, Achim and Gabor Grothendieck (2005). zoo: S3 Infrastructure for Regular and Irregular Time Series. Journal of Statistical Software, 14(6), 1-27. doi:10.18637/jss.v014.i06
- Zhu, Hao (2021). kableExtra: Construct Complex Table with 'kable' and Pipe Syntax. R package version 1.3.4. https://CRAN.R-project.org/package=kableExtra

Python Packages Used:
- Bradski, G. (2000). The OpenCV Library. Dr. Dobb&#x27;s Journal of Software Tools.
- Harris, C.R., Millman, K.J., van der Walt, S.J. et al. Array programming with NumPy. Nature 585, 357–362 (2020). DOI: 10.1038/s41586-020-2649-2. (Publisher link).
- Hunter, J. D. (2007), Matplotlib: A 2D graphics environment. Computing In Science & Engineering 9.3 90-95.
- Librealsense TM - pyrealsense2
- The pandas development team. (2022). pandas-dev/pandas: Pandas (v1.5.1). Zenodo. https://doi.org/10.5281/zenodo.7223478
- Pauli Virtanen, Ralf Gommers, Travis E. Oliphant, Matt Haberland, Tyler Reddy, David Cournapeau, Evgeni Burovski, Pearu Peterson, Warren Weckesser, Jonathan Bright, Stéfan J. van der Walt, Matthew Brett, Joshua Wilson, K. Jarrod Millman, Nikolay Mayorov, Andrew R. J. Nelson, Eric Jones, Robert Kern, Eric Larson, CJ Carey, İlhan Polat, Yu Feng, Eric W. Moore, Jake VanderPlas, Denis Laxalde, Josef Perktold, Robert Cimrman, Ian Henriksen, E.A. Quintero, Charles R Harris, Anne M. Archibald, Antônio H. Ribeiro, Fabian Pedregosa, Paul van Mulbregt, and SciPy 1.0 Contributors. (2020) SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nature Methods, 17(3), 261-272.
- Python Foundation packages: argparse, csv, glob, itertools, json, os, pickle, re, shutil, subprocess, sys, time, traceback

## Contact us ##
For additional infomation and guidance, contact the 3DSR team @:
* Doron Shiffer-Sebba (doron@northwestern.edu)
* Nicolas Legewie (nicolas.legewie@uni-erfurt.de)
* Yoav Goldstein (yoav.goldstein@mail.huji.ac.il)
