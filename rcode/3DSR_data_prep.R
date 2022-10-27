###************************************************************ ###
###************************************************************ ###
##### 3DSR Data Preparation - Prepare 3D Videos for Analysis #####
###************************************************************ ###
###************************************************************ ###

# Install and Load Necessary R Packages
if (!require("pacman")) {
  install.packages(
    "pacman",
    repos = "http://cran.us.r-project.org"
  )
}
pacman::p_load(
  tidyverse,
  zoo,
  naniar,
  data.table,
  slider,
  ggplot2
)

# Make sure there is at least one argument (directory with videos)
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("At least one argument must be supplied (input file).n", call. = FALSE)
}

# Define paths
your_path <- args[1]

path_input <- file.path(your_path, "Inputs")

path_output <- file.path(your_path, "Outputs")

###****************** ###
##### Read in data #####
###****************** ###

# Read in names of files

file <- scan(file.path(path_input, "csv_list.txt"), what = list(""))

csv_names <- as.list(file[[1]])


# Combine keypoints and confidence tables into one master df

make_df_list <- function(name, type) {
  if (type == "keypoints") {
    new_name <- str_sub(name, 8)
    return(tibble(read_csv(file.path(path_input, new_name))))
  } else {
    new_name <- str_c(str_sub(name, 8, -5), "_confidence.csv")
    return(tibble(read_csv(file.path(path_input, new_name))))
  }
}

shorten_video_name <- function(name) {
  return(str_sub(name, 8, -5))
}

df <-
  as_tibble_col(
    unlist(csv_names),
    column_name = "name"
  ) %>%
  mutate(
    df_list = map2(name, "keypoints", make_df_list),
    df_list_confidence = map2(name, "confidence", make_df_list),
    name = unlist(map(name, shorten_video_name))
  )


###*********************** ###
##### Rename df columns #####
###*********************** ###

rename_cols_fun <- function(df, type) {
  if (type == "keypoints") {
    df <- df %>%
      rename(
        frame = frameiD,
        pid = bodyiD
      )
    df <- df %>%
      rename_with(str_replace, names(df), "l_smalltoe", "crown_head")
    df <- df %>%
      rename_with(str_replace, names(df), "l_bigtoe", "thorax")
  } else {
    df <- df %>%
      rename(
        frame = FrameID,
        pid = BodyID
      )
    df <- df %>%
      rename_with(
        str_replace, names(df), "LSmallToe_Confidence",
        "CrownHead_Confidence"
      )
  }
  return(df %>%
    select(frame, pid, everything()))
}

df <- df %>%
  mutate(
    df_list = map2(df_list, "keypoints", rename_cols_fun),
    df_list_confidence = map2(
      df_list_confidence,
      "confidence", rename_cols_fun
    )
  )

delete_extra_pids <- function(x) {
  x %>%
    filter(pid %in% c(0, 1))
} # Deletes two frames across 13 paper videos

df <- df %>%
  mutate(
    df_list = map(df_list, delete_extra_pids),
    df_list_confidence = map(df_list_confidence, delete_extra_pids)
  )


###************************ ###
##### Replace 0's as NA's #####
###************************ ###

replace_na_fun <- function(x) {
  x %>%
    mutate(across(where(is.numeric), ~ na_if(., 0))) %>%
    mutate(pid = ifelse(is.na(pid), 0, 1))
}

df <- df %>%
  mutate(df_list = map(df_list, replace_na_fun))


###************************************************* ###
##### Create potential misclassification indicator #####
###************************************************* ###

# Reshape data frame for easier computing of keypoint deltas
reshape_for_misclassification <- function(x) {
  x %>%
    pivot_longer(-c(pid, frame),
      names_to = "keypoint",
      values_to = "value"
    ) %>%
    separate(keypoint,
      into = c("keypoint", "axis"),
      sep = -1
    ) %>%
    group_by(pid) %>%
    pivot_wider(
      names_from = pid,
      values_from = value,
      names_prefix = "person"
    )
}

df <- df %>%
  mutate(df_list_for_misclassification =
        map(df_list, reshape_for_misclassification))


# Create data frame with lagged keypoint values
reshape_misclassification_lag <- function(x) {
  x %>%
    # Create lagged keypoint values
    group_by(pid) %>%
    mutate(across(
      -c(frame),
      lag
    )) %>%
    ungroup() %>%
    # Reshape data frame for easier computing of keypoint deltas
    pivot_longer(-c(pid, frame),
      names_to = "keypoint",
      values_to = "value"
    ) %>%
    separate(keypoint,
      into = c("keypoint", "axis"),
      sep = -1
    ) %>%
    pivot_wider(
      names_from = pid,
      values_from = value,
      names_prefix = "person_lagged"
    )
}


df <- df %>%
  mutate(df_list_for_misclassification_lagged =
        map(df_list, reshape_misclassification_lag))


# Join standard and lagged dfs
join_for_misclassification <- function(x, y) {
  x %>%
    left_join(y)
}

df <- df %>%
  mutate(df_list_for_misclassification_joined = map2(
    df_list_for_misclassification,
    df_list_for_misclassification_lagged,
    join_for_misclassification
  ))


# Compute euclidean distance

get_euclidean <- function(a, b) {
  sqrt(sum((a - b)^2))
}

get_euclidean_for_df <- function(x) {
  x %>%
    group_by(frame, keypoint) %>%
    summarize(
      euclidean_distance_betw_persons = get_euclidean(person0, person1),
      euclidean_distance_person0_betw_frames =
                                        get_euclidean(person0, person_lagged0),
      euclidean_distance_person1_betw_frames =
                                        get_euclidean(person1, person_lagged1)
    ) %>%
    ungroup()
}

df <- df %>%
  mutate(df_list_euclidean_for_misclassification = map(
    df_list_for_misclassification_joined,
    get_euclidean_for_df
  ))


# Create misclassification index
create_misclass_index <- function(x) {
  x %>%
    mutate(
      misclassification_person0 =
        case_when(
          euclidean_distance_betw_persons >
                                  euclidean_distance_person0_betw_frames ~ 0,
          euclidean_distance_betw_persons <
                                  euclidean_distance_person0_betw_frames ~ 1,
          TRUE ~ NA_real_
        ),
      misclassification_person1 =
        case_when(
          euclidean_distance_betw_persons >
                                  euclidean_distance_person1_betw_frames ~ 0,
          euclidean_distance_betw_persons <
                                  euclidean_distance_person1_betw_frames ~ 1,
          TRUE ~ NA_real_
        )
    ) %>%
    # Select relevant columns
    select(frame, keypoint, misclassification_person0,
                            misclassification_person1) %>%
    # Reshape data frame
    pivot_longer(c(misclassification_person0, misclassification_person1),
      names_to = "pid",
      values_to = "misclassification"
    ) %>%
    # Recode pid to original form (double vector of 0 and 1)
    mutate(pid = ifelse(str_detect(pid, "0"), 0, 1)) %>%
    # Reshape data frame
    pivot_wider(
      names_from = "keypoint",
      values_from = "misclassification"
    ) %>%
    # Rename keypoint columns
    rename_with(~ str_c(., "X"), .cols = crown_head:thorax)
}

df <- df %>%
  mutate(
    df_list_misclassifications =
      map(
        df_list_euclidean_for_misclassification,
        create_misclass_index
      )
  ) %>%
  select(-c(
    df_list_euclidean_for_misclassification,
    df_list_for_misclassification_joined,
    df_list_for_misclassification_lagged,
    df_list_for_misclassification
  ))


# Add misclassified row index and expand to three keypoints
add_and_expand <- function(x) {
  x %>%
    mutate(misclassified = 1) %>%
    left_join(x %>%
    rename_with(~ str_replace(., "X", "Y"))) %>%
    left_join(x %>% rename_with(~ str_replace(., "X", "Z")))
}

df <- df %>%
  mutate(
    df_list_misclassifications_expanded =
      map(df_list_misclassifications, add_and_expand))


# Replace misclassifications as NA
set_misclassifications_na <- function(na_rep, misclassification_expanded) {
  na_rep <- na_rep %>%
    mutate(misclassified = 0) %>%
    rbind(misclassification_expanded) %>%
    select(frame, pid, misclassified, everything()) %>%
    arrange(frame, pid, misclassified) %>%
    mutate(across(-c(frame, pid, misclassified), ~ case_when(
      misclassified == 0 & lead(., 1) == 1 ~ NA_real_,
      TRUE ~ .
    ))) %>%
    filter(misclassified == 0) %>%
    select(-misclassified)
}

df <- df %>%
  mutate(df_list = map2(
    df_list,
    df_list_misclassifications_expanded,
    set_misclassifications_na
  )) %>%
  select(-df_list_misclassifications_expanded)


###****************************** ###
##### Fill up implicit missings #####
###****************************** ###

expand_dfs_fun <- function(x) {
  x %>%
  right_join(x %>%
  expand(frame, pid))
}

df <- df %>%
  mutate(
    df_list = map(
      df_list,
      expand_dfs_fun
    ),
    df_list_confidence = map(
      df_list_confidence,
      expand_dfs_fun
    )
  )


###******************* ###
##### pid as factor #####
###******************* ###

pid_to_fac_fun <- function(x) {
  x %>%
  mutate(pid = as_factor(pid))
}


df <- df %>%
  mutate(
    df_list = map(
      df_list,
      pid_to_fac_fun
    ),
    df_list_confidence = map(
      df_list_confidence,
      pid_to_fac_fun
    )
  )


###*************************************** ###
##### Create moving median for keypoints #####
###*************************************** ###

mov_med_fun <- function(x) {
  x %>%
    group_by(pid) %>%
    arrange(frame) %>%
    mutate(across(-frame, ~ slide_vec(.x, median,
                                      .before = 4, .complete = TRUE))) %>%
    ungroup()
}

df <- df %>%
  mutate(
    df_list_mov_med = map(
      df_list,
      mov_med_fun
    )
  )

###******************* ###
##### GENERATE DATA #####
###******************* ###

###******************************************************* ###
#####    Distance Moved Between Frames, per Keypoint    #####
###******************************************************* ###

move_dist_fun <- function(x) {
  x %>%
    group_by(pid) %>%
    mutate(across(noseX:crown_headZ,
      ~ . - lag(., 1),
      .names = "distLag1_{.col}"
    )) %>%
    select(-(noseX:crown_headZ)) %>%
    ungroup()
}

df <- df %>%
  mutate(
    df_list_mov_dist = map(
      df_list_mov_med,
      move_dist_fun
    )
  ) %>%
  select(-df_list_mov_med)


###******************************* ###
##### Create missing data frame #####
###******************************* ###

create_miss_fun <- function(x) {
  x %>%
    select(frame, pid, contains("X")) %>%
    rename_with(str_remove, everything(), "X") %>%
    add_any_miss()
}

df <- df %>%
  mutate(df_list_for_missing = map(
    df_list,
    create_miss_fun
  ))


###*************************************** ###
#####    Add Thorax Distance Measures    #####
###*************************************** ###

get_csv <- function(name) {
  file_name <- file.path(path_input,
                        str_c("thorax_dist_", name, ".csv"))
  df <- read_csv(file_name) %>%
    rename(frame = FrameID) %>%
    filter(!is.na(Thorax_dist))
}

df <- df %>%
  mutate(figure_two_files = map(
    name,
    get_csv
  ))


###***************************** ###
#####    Make Body Part DFs    #####
###***************************** ###

make_bodypart_data <- function(df) {
  df <- df %>%
    mutate(pid = if_else(pid == 1, 1, 0)) %>%
    rowwise() %>%
    abs() %>%
    summarise(
      pid = pid,
      frame = frame,
      total_movement = mean(c_across(distLag1_noseX:distLag1_crown_headZ),
                                      na.rm = TRUE),
      total_movement_head = mean(c_across(contains(c(
                              "nose", "crown", "neck", "eye", "ear"))),
                                          na.rm = TRUE),
      total_movement_torso = mean(c_across(contains(c(
                              "shoulder", "thorax", "hip"))),
                                          na.rm = TRUE),
      total_movement_arms = mean(c_across(contains(c(
                              "elbow", "wrist"))),
                                          na.rm = TRUE),
      total_movement_legs = mean(c_across(contains(c(
                              "knee", "ankle"))),
                                          na.rm = TRUE)
    )
}

df <- df %>%
  mutate(bodypart_df = map(
    df_list_mov_dist,
    make_bodypart_data
  ))


### ************************************************* ###
#####    Identify each df's first non-zero frame    #####
### ************************************************* ###

first_non_zero_frame <- function(df) {

  first_non_zero_frame <-
    df %>%
    filter(total_movement != 0) %>%
    slice_head() %>%
    select(frame)
    first_non_zero_frame[[1, 1]]
}

df <- df %>%
  mutate(first_frame = map(
    bodypart_df,
    first_non_zero_frame
  ))

###********************* ###
##### SAVE DATA FILES #####
###********************* ###

save(df,
  file = file.path(path_input, "master_df.rdata")
)

print("All done! Saved master_df.rdata to Inputs folder.")

