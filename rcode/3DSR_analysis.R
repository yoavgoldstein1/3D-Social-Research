
###************************************* ###
###************************************* ###
##### ***** 3DSR@SMR - ANALYSIS ***** #####
###************************************* ###
###************************************* ###

###*************** ###
##### LIBRARIES #####
###*************** ###

if (!require("pacman")) {
  install.packages("pacman", repos = "http://cran.us.r-project.org")
}
pacman::p_load(
  tidyverse,
  grid,
  gridExtra,
  zoo,
  naniar,
  sjPlot,
  cowplot,
  data.table,
  kableExtra,
  patchwork,
  gganimate,
  gifski,
  glue
)


###********************************* ###
##### PATHS, FILES & OUTPUT NAMES #####
###********************************* ###

args <- commandArgs(trailingOnly = TRUE)
# test if there is at least one argument: if not, return an error
if (length(args) == 0) {
  stop("At least one argument must be supplied (input file).n", call. = FALSE)
}

# Define paths
your_path <- args[1]

path_input <- file.path(your_path, "Inputs")

path_output <- file.path(your_path, "Outputs")


###****************** ###
##### READ IN DATA #####
###****************** ###

load(file.path(path_input, "master_df.rdata"))


###*********************************** ###
#####    COMBINE SCRIPTED VIDEOS?    #####
###*********************************** ###

scripted_check_list <-
  df$name %>%
  map(str_detect, "Final", negate = TRUE)

scripted_videos <- TRUE %in% scripted_check_list


###****************************************** ###
#####    DEFINE COLOR SCHEME FOR FIGURES    #####
###****************************************** ###

color_blind_figure3_5_6 <- c("#F0E442", "#CC79A7")

color_blind_figure7 <- c("#F0E442", "#CC79A7", "#56B4E9", "#009E73")


###****************************************************************************** ###
##### FIGURE 2s: Distance between two individuals’ thorax keypoints over frames #####
###****************************************************************************** ###

print("Working on F2s!")

create_figure_two <- function(df, first_frame) {

  ##### Create plot #####

  df %>%
    ggplot(aes(x = frame, y = Thorax_dist)) +
    geom_line() +
    geom_smooth(se = FALSE) +
    labs(
      y = "distance between persons (meters)",
      x = ""
    ) +
    xlim(first_frame, NA) +
    theme_light() +
    theme(text = element_text(size = 15))
}


figure_twos <- function(df, name, first_frame) {
  df <- create_figure_two(df, first_frame)

  ##### Save figure 2 #####

  save_name <- str_c(name, "_f2.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 8,
    height = 6
  )
}


pmap(list(df$figure_two_files, df$name, df$first_frame), figure_twos)


if (scripted_videos == TRUE) {

  extract_first_frame <- function(df, video) {
    first_frame <- df %>%
    filter(name == video) %>%
    select(first_frame) %>%
    unnest(first_frame)

  }

  # Create figures
  first_frame <- extract_first_frame(df, "clean_D415_Far_Light")
  fig2a <-
    df %>%
    filter(name == "clean_D415_Far_Light") %>%
    select(figure_two_files) %>%
    unnest(figure_two_files) %>%
    create_figure_two(first_frame[[1]]) +
    labs(title = "A")

  first_frame <- extract_first_frame(df, "clean_0_540_Final")
  fig2b <-
    df %>%
    filter(name == "clean_0_540_Final") %>%
    select(figure_two_files) %>%
    unnest(figure_two_files) %>%
    create_figure_two(first_frame[[1]]) +
    ylab("") +
    labs(title = "B")

  # Create figure layout
  fig2a + fig2b +
    ylim(0, 3.5)

  # Save figure 2
  ggsave("Goldstein_etal_figure2.pdf",
    device = "pdf", path = path_output,
    width = 12,
    height = 8
  )
}

###*************************************************** ###
##### FIGURE 3s: Continuous position of individuals ######
###*************************************************** ###

print("Working on F3s!")

prep_for_animation <- function(df) {
  df <-
    df %>%
    pivot_longer(noseX:crown_headZ,
      names_to = "keypoint",
      values_to = "value"
    ) %>%
    separate(keypoint,
      into = c(
        "keypoint",
        "axis"
      ),
      sep = -1
    ) %>%
    group_by(frame, pid, axis) %>%
    summarize(mean_value = mean(value, na.rm = TRUE)) %>%
    ungroup() %>%
    pivot_wider(
      names_from = axis,
      values_from = mean_value
    ) %>%
    na.omit()
}


get_euclidean <- function(a, b) {
  sqrt(sum((a - b)^2))
}


prep_for_animation_3 <- function(df) {
  df_for_animation <- prep_for_animation(df)

  df_for_animation %>%
    pivot_longer(X:Z,
      names_to = "axis",
      values_to = "value"
    ) %>%
    pivot_wider(
      names_from = pid,
      values_from = value
    ) %>%
    rename(
      person0 = `0`,
      person1 = `1`
    ) %>%
    group_by(frame) %>%
    mutate(euclidean = get_euclidean(person0, person1)) %>%
    left_join(df_for_animation) %>%
    select(-c(person0, person1))
}


figure_threes <- function(df, name) {

  ##### Create plot #####

  df <- prep_for_animation_3(df) %>%
    ggplot(aes(x = X, y = Z, color = factor(pid))) +
    theme_light() +
    geom_point(size = 5) +
    geom_text(
      aes(y = 0.2, x = -6.5, label = glue("frame: {frame}")),
      family = "Merriweather Sans",
      size = 6,
      color = "black",
      hjust = -0.2
    ) +
    geom_text(
      aes(y = 0.2, x = 2, label = glue("distance: {round(euclidean, 2)}m")),
      family = "Merriweather",
      size = 6,
      color = "black"
    ) +
    labs(
      y = "",
      x = ""
    ) +
    scale_color_discrete(
      name = "",
      labels = c("Person 1", "Person 2"),
      type = color_blind_figure3_5_6
    ) +
    guides(color = guide_legend(override.aes = list(fill = "#FFFFFF"))
    ) +
    theme(
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank()
    ) +
    transition_reveal(frame)


  ##### Save Figure 3 #####

  save_name <- str_c(name, "_f3.gif")

  animate(df, renderer = gifski_renderer())
  anim_save(save_name,
    path = path_output
  )
}


df$df_list %>%
  map2(df$name, figure_threes)


###************************************************************************ ###
##### FIGURE 4s: Frequency of physical distance states over video frames ######
###************************************************************************ ###

print("Working on F4s!")

calculate_space <- function(df) {
  df <- df %>%
    pivot_longer(X:Z,
      names_to = "axis",
      values_to = "value"
    ) %>%
    pivot_wider(
      names_from = pid,
      values_from = value
    ) %>%
    rename(
      person0 = `0`,
      person1 = `1`
    ) %>%
    group_by(frame) %>%
    mutate(euclidean = get_euclidean(person0, person1)) %>%
    left_join(df) %>%
    select(frame, euclidean) %>%
    distinct()
}


figure_fours <- function(df, name) {

  ##### Hall's distance categories #####
  intimate_distance_lower <- 0
  intimate_distance_upper <- 0.46
  personal_distance_lower <- 0.47
  personal_distance_upper <- 1.22
  social_distance_lower <- 1.23
  social_distance_upper <- 3.66
  public_distance_lower <- 3.67
  public_distance_upper <- 7.62

  ##### Generate first plot #####

  space_categories_plot <- df %>%
    prep_for_animation() %>%
    calculate_space() %>%
    filter(!is.na(euclidean)) %>%
    mutate(distance_category = case_when(
      between(
        round(euclidean, 2),
        intimate_distance_lower,
        intimate_distance_upper
      ) ~ "intimate distance",
      between(
        round(euclidean, 2),
        personal_distance_lower,
        personal_distance_upper
      ) ~ "personal distance",
      between(
        round(euclidean, 2),
        social_distance_lower,
        social_distance_upper
      ) ~ "social distance",
      between(
        round(euclidean, 2),
        public_distance_lower,
        public_distance_upper
      ) ~ "public distance"
    )) %>%
    ggplot(aes(distance_category)) +
    geom_bar(aes(y = (..count..) / sum(..count..))) +
    scale_y_continuous(
      labels = scales::percent,
      limits = c(0, 1)
    ) +
    ylab("relative frequencies") +
    xlab("") +
    labs(
      title = "A: Categories of space",
      subtitle = "(following Hall 1966)"
    ) +
    theme_light()

  ##### Generate second plot #####

  covid_threshold <- 1.5

  covid_threshold_plot <- df %>%
    prep_for_animation() %>%
    calculate_space() %>%
    filter(!is.na(euclidean)) %>%
    mutate(distancing_violation = ifelse(
            euclidean < covid_threshold, "violation", "no violation")) %>%
    ggplot(aes(distancing_violation)) +
    geom_bar(aes(y = (..count..) / sum(..count..))) +
    scale_y_continuous(
      labels = scales::percent,
      limits = c(0, 1)
    ) +
    ylab("") +
    xlab("") +
    labs(
      title = "B: Social distancing violations",
      subtitle = "(1.5m threshold)"
    ) +
    theme_light()

  ##### Display both plots #####

  space_categories_plot + covid_threshold_plot

  ##### Save figure 4 #####

  save_name <- str_c(name, "_f4.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 12,
    height = 6
  )
}

df$df_list %>%
  map2(df$name, figure_fours)


###*************************************************************************** ###
##### FIGURE 5s: Bird’s eye view of individuals’ movement in space over time #####
###*************************************************************************** ###

print("Working on F5s!")

create_figure_five <- function(df) {
  figure <- df %>%
    select(frame, pid, noseX, noseY, noseZ) %>%
    ggplot(aes(x = noseX, y = noseZ, color = factor(pid))) +
    theme_light() +
    geom_point(alpha = 0.4) +
    labs(
      y = "",
      x = ""
    ) +
    scale_color_discrete(
      name = "",
      labels = c("Person 1", "Person 2"), 
      type = color_blind_figure3_5_6
    ) +
    guides(color = guide_legend(override.aes = list(fill = "#FFFFFF"))
    ) +
    theme(
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank()
    )
}


figure_fives <- function(df, name) {
  figure <- create_figure_five(df)

  save_name <- str_c(name, "_f5.pdf")

  ggsave(save_name,
    device = "pdf", path = path_output,
    width = 12,
    height = 6
  )
}


# Make and save figure 5's

df$df_list %>%
  map2(df$name, figure_fives)



# Official figure for paper

if (scripted_videos == TRUE) {

  # Create figure 5a
  fig5a <-
    df %>%
    filter(name == "clean_D415_Far_Light") %>%
    select(df_list) %>%
    unnest(df_list) %>%
    filter(frame < 2500) %>%
    create_figure_five() +
    labs(title = "A") +
    theme(
      legend.text = element_text(size = 12),
      legend.position = c(0.25, 0.15),
      legend.direction = "horizontal"
    ) +
    guides(colour = guide_legend(override.aes = list(alpha = 1)))

  # Create figure 5b
  fig5b <-
    df %>%
    filter(name == "clean_D415_Far_Light") %>%
    select(df_list) %>%
    unnest(df_list) %>%
    filter(frame > 2500) %>%
    create_figure_five() +
    labs(title = "B") +
    theme(
      legend.text = element_text(size = 12),
      legend.position = c(0.25, 0.15),
      legend.direction = "horizontal"
    ) +
    guides(colour = guide_legend(override.aes = list(alpha = 1)))

  # Create figure 5c
  fig5c <-
    df %>%
    filter(name == "clean_0_540_Final") %>%
    select(df_list) %>%
    unnest(df_list) %>%
    create_figure_five() +
    labs(title = "C") +
    theme(
      legend.text = element_text(size = 12),
      legend.position = c(0.25, 0.15),
      legend.direction = "horizontal"
    ) +
    guides(colour = guide_legend(override.aes = list(alpha = 1)))

  # Create figure layout
  (fig5a | fig5b) / (fig5c | plot_spacer())

  # Save figure 5
  ggsave("Goldstein_etal_figure5.pdf",
    device = "pdf", path = path_output,
    width = 12,
    height = 8
  )
}


###***************************************************************************** ###
##### FIGURE 6s: Comparison of aggregate movement of all keypoints over frames #####
###***************************************************************************** ###

print("Working on F6s!")

##### Summarize data #####

create_figure_six <- function(df, first_frame) {
  pid_labs <- c("Person 1", "Person 2")
  names(pid_labs) <- c(0, 1)

  df %>%
    ggplot(aes(x = frame, y = total_movement, color = as_factor(pid))) +
    xlim(first_frame, NA) +
    ylim(0, 0.3) +
    geom_line() +
    geom_smooth(color = "grey30", se = FALSE) +
    labs(
      y = "mean movement (meters)",
      x = ""
    ) +
    theme_light() +
    theme(
      legend.position = "none",
      text = element_text(size = 20)
    ) +
    facet_grid(. ~ pid, labeller = labeller(pid = pid_labs)) +
    scale_color_discrete(type = color_blind_figure3_5_6) +
    guides(color = NULL)
}

figure_sixs <- function(df, name, first_frame) {
  df <- create_figure_six(df, first_frame)

  save_name <- str_c(name, "_f6.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 10,
    height = 6
  )
}


pmap(list(df$bodypart_df, df$name, df$first_frame), figure_sixs)


if (scripted_videos == TRUE) {

  # Create figures
  fig6a <-
    df %>%
    filter(name == "clean_D415_Far_Light") %>%
    select(bodypart_df) %>%
    unnest(bodypart_df) %>%
    create_figure_six(540) +
    ylim(0, 0.1) +
    labs(title = "A") +
    guides(color = "none")

  fig6b <-
    df %>%
    filter(name == "clean_0_540_Final") %>%
    select(bodypart_df) %>%
    unnest(bodypart_df) %>%
    create_figure_six(341) +
    labs(title = "B") +
    guides(color = "none")

  # Create figure layout
  fig6a / fig6b

  # Save figure 6
  ggsave("Goldstein_etal_figure6.pdf",
    device = "pdf", path = path_output,
    width = 12,
    height = 8
  )
}


###************************************************************************** ###
##### FIGURE 7s: Comparison of aggregate movement of body parts over frames #####
###************************************************************************** ###

print("Working on F7s!")

create_figure_seven <- function(df, first_frame) {
  pid_labs <- c("Person 1", "Person 2")
  names(pid_labs) <- c(0, 1)

  df <- df %>%
    pivot_longer(
      cols = total_movement_head:total_movement_legs,
      names_to = "bodyParts",
      values_to = "total_movement_parts"
    )

  ##### Create plot #####

  df %>%
    ggplot(aes(x = frame, y = total_movement_parts, color = bodyParts)) +
    xlim(first_frame, NA) +
    ylim(0, 0.8) +
    geom_line(alpha = 0.4) +
    geom_smooth() +
    labs(
      y = "mean movement (meters)",
      color = "Body part",
      x = ""
    ) +
    theme_light() +
    theme(text = element_text(size = 20)) +
    facet_grid(. ~ pid, labeller = labeller(pid = pid_labs)) +
    scale_color_discrete(labels = c(
      "Arms",
      "Head",
      "Legs",
      "Torso"
    ),
      type = color_blind_figure7) +
    guides(color = guide_legend(override.aes = list(fill = "#FFFFFF")))
}


figure_sevens <- function(df, name, first_frame) {
  df <- create_figure_seven(df, first_frame)

  ##### Save figure 7 #####

  save_name <- str_c(name, "_f7.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 10,
    height = 6
  )
}


pmap(list(df$bodypart_df, df$name, df$first_frame), figure_sevens)


if (scripted_videos == TRUE) {

  # Create plots
  fig7a <-
    df %>%
    filter(name == "clean_D415_Far_Light") %>%
    select(bodypart_df) %>%
    unnest(bodypart_df) %>%
    create_figure_seven(540) +
    ylim(0, 0.1) +
    labs(title = "A")

  fig7b <-
    df %>%
    filter(name == "clean_0_540_Final") %>%
    select(bodypart_df) %>%
    unnest(bodypart_df) %>%
    create_figure_seven(341) +
    ylim(0, 0.5) +
    labs(title = "B")


  # Create figure layout
  fig7a / fig7b

  # Save figure 7
  ggsave("Goldstein_etal_figure7.pdf",
    device = "pdf", path = path_output,
    width = 12,
    height = 8
  )
}


###********************************************** ###
##### TABLE 2: Reliability comparison of videos #####
###********************************************** ###

print("Working on T2!")

### 1. Missing Every KP ###

create_miss_general_fun <- function(df) {
  bind_cols(
    df %>%
      add_n_miss() %>%
      summarize(
        total_miss = sum(n_miss_all),
        total_keypoints = n() * 21
      ),
    df %>%
      add_n_miss() %>%
      mutate(all_missing = ifelse(n_miss_all == 21, 1, 0)) %>%
      summarize(
        sum_all_missing = sum(all_missing),
        perc_all_missing = sum(all_missing) / n()
      )
  ) %>%
    pivot_longer(everything(),
      names_to = "stat",
      values_to = "value"
    )
}

select_value <- function(x) {
  x <- x$value[[4]]
}

df <- df %>%
  mutate(
    df_list_miss_general =
      map(df$df_list_for_missing, create_miss_general_fun),
    pct_all_missing = map(
      df_list_miss_general,
      select_value
    )
  ) %>%
  select(-df_list_miss_general)


### 2. Missing Some KP ###

df <- df %>%
  mutate(missing_kp = map(df$df_list_for_missing, pct_miss))


### 3. Confidence ###

overall_conf_fun <- function(df) {
  df %>%
    summarize(across(contains("Confidence"), mean, na.rm = TRUE)) %>%
    sum() / 21
}

df <- df %>%
  mutate(
    overall_confidenceMean =
      map(df_list_confidence, overall_conf_fun)
  )


##### 4. Misclassification #####

get_misclassification_sum <- function(x) {
  x %>%
    select(-c(frame, pid)) %>%
    mutate(misclassification_sum = rowSums(., na.rm = TRUE)) %>%
    summarize(misclassification_total = sum(misclassification_sum)) %>%
    pull()
}

df <- df %>%
  mutate(
    misclassification_sum =
      map(df_list_misclassifications, get_misclassification_sum)
  )


##### 5. Save Table #####

table2 <- df %>%
  select(c(
    name,
    missing_kp,
    pct_all_missing,
    misclassification_sum,
    overall_confidenceMean
  )) %>%
  unnest(-name)

pdf(
  file = file.path(
    path_output,
    "Goldstein_etal_table2.pdf"
  ),
  height = 4, width = 14
)
grid.table(table2)
dev.off()

# Sub-headers were added manually

table2 %>%
  tab_df(col.header = c(
    "Video",
    "% missing",
    "% all missing",
    "N of misclassifications",
    "Confidence (mean)"
  ))



###********************************************************* ###
##### TABLE 3: Reliability comparison by recording feature #####
###********************************************************* ###

print("Working on T3!")

if (scripted_videos == TRUE) {
  table3 <- table2 %>%
    filter(unlist(scripted_check_list)) %>%
    mutate(
      camera =
        case_when(
          str_detect(name, "D415") ~ "D415",
          str_detect(name, "L515") ~ "L515"
        ),
      distance =
        case_when(
          str_detect(name, "Far") ~ "Far",
          str_detect(name, "Close") ~ "Close"
        ),
      lighting =
        case_when(
          str_detect(name, "Light") ~ "Light",
          str_detect(name, "Dark") ~ "Dark"
        ),
      angle =
        case_when(
          str_detect(name, "Side") ~ "Side",
          str_detect(name, "Final", negate = TRUE) &
            str_detect(name, "Side", negate = TRUE) ~ "Front"
        )
    )

  ##### GROUPINGS FUNCTIONS #####

  # Camera
  create_camera_comp_fun <- function(x) {
    x %>%
      group_by(camera) %>%
      filter(!str_detect(name, "Side") & !str_detect(name, "Dark"))
  }

  # Distance
  create_distance_comp_fun <- function(x) {
    x %>%
      group_by(distance) %>%
      filter(!str_detect(name, "Side") & !str_detect(name, "Dark"))
  }

  # Lighting
  create_lighting_comp_fun <- function(x) {
    x %>%
      group_by(lighting) %>%
      filter(!str_detect(name, "Side") & !str_detect(name, "Close"))
  }

  # Angle
  create_angle_comp_fun <- function(x) {
    x %>%
      group_by(angle) %>%
      filter(!str_detect(name, "D415") & !str_detect(
        name,
        "L515_Far_Light"
      ))
  }

  ##### Define group comparison function #####

  create_group_comp_table_fun <- function(x, comp_dim) {
    x %>%
      summarize(
        pct_missing_mean = mean(missing_kp),
        pct_all_missing_mean = mean(pct_all_missing),
        n_misclass_mean = mean(misclassification_sum),
        mean_confidence_mean = mean(overall_confidenceMean)
      ) %>%
      # n_pidSwitches_mean = mean(n_pidSwitches)) %>%
      mutate(comparison = as.character(comp_dim)) %>%
      rename(group = comp_dim) %>%
      select(comparison, everything())
  }

  ##### Bind table #####

  table3 <- bind_rows(
    table3 %>%
      create_camera_comp_fun() %>%
      create_group_comp_table_fun("camera"),
    table3 %>%
      create_distance_comp_fun() %>%
      create_group_comp_table_fun("distance"),
    table3 %>%
      create_lighting_comp_fun() %>%
      create_group_comp_table_fun("lighting"),
    table3 %>%
      create_angle_comp_fun() %>%
      create_group_comp_table_fun("angle")
  )

  ##### Save table 3 #####
  pdf(
    file = file.path(
      path_output,
      "Goldstein_etal_table3.pdf"
    ),
    height = 4, width = 14
  )
  grid.table(table3)
  dev.off()
}

##### Draw table #####

table3 %>% tab_df(col.header = c(
  "Comparison",
  "Group",
  "% missing (mean)",
  "% all missing (mean)",
  "N of misclassifications (mean)",
  "Mean confidence (mean)"
))
# "N of PID switches (mean)"))


###********************************************************* ###
##### FIGURE A1: Percentage of missing values by keypoint ######
#*********************************************************** ###

print("Working on A1s!")

missing_perc_by_pid <- function(df, name) {
  pid_labs <- c("Person 1", "Person 2")
  names(pid_labs) <- c(0, 1)

  df %>%
    select(-c(any_miss_all, frame)) %>%
    group_by(pid) %>%
    miss_var_summary() %>%
    ggplot(aes(x = variable, y = pct_miss)) +
    geom_segment(aes(
      x = variable,
      xend = variable,
      y = 0,
      yend = pct_miss
    ), color = "gray80") +
    geom_point(color = "gray40", size = 3) +
    theme_light() +
    coord_flip() +
    theme(
      panel.grid.major.y = element_blank(),
      panel.border = element_blank(),
      axis.ticks.y = element_blank()
    ) +
    facet_wrap(. ~ pid, labeller = labeller(pid = pid_labs)) +
    labs(title = name) +
    ylab("% of missing values") +
    xlab("") +
    theme(plot.margin = margin(
      t = 0.5, r = 0, b = 0.5, l = 0, unit =
        "cm"
    ))

  ##### Save figures A1 #####

  save_name <- str_c(name, "_a1.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 6,
    height = 8
  )
}

df$df_list_for_missing %>%
  map2(df$name, missing_perc_by_pid)


###****************************************************************** ###
##### FIGURE A2s: Overall proportion of keypoints missing per frame #####
###****************************************************************** ###

print("Working on A2s!")

appendix_twos <- function(df, name, first_frame) {

  ##### Prepare Data #####

  df <-
    df %>%
    select(-frame, -pid, -any_miss_all) %>%
    prop_miss_row() %>%
    bind_cols(df %>%
        select(frame, pid)) %>%
    rename(pct_missing = ...1)

  ##### Create plot #####

  df %>%
    ggplot(data = ., aes(frame, pct_missing, color = 1)) +
    theme_light() +
    geom_smooth(se = FALSE) +
    guides(color = FALSE) +
    ylab("") +
    xlab("") +
    xlim(first_frame, NA) +
    ggtitle("Proportion of missing keypoints over frames")

  ##### Save figure A2 #####

  save_name <- str_c(name, "_a2.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 10,
    height = 6
  )
}

pmap(list(df$df_list_for_missing, df$name, df$first_frame), appendix_twos)



###*************************************************** ###
##### FIGURE A3s: Mean confidence value by keypoint ######
###*************************************************** ###

print("Working on A3s!")

appendix_threes <- function(df, name) {

  ##### Prepare Data #####

  df <- df %>%
    summarize(across(contains("Confidence"), mean, na.rm = TRUE)) %>%
    pivot_longer(
      cols = everything(),
      names_to = "keypoint",
      values_to = "confidence_mean"
    ) %>%
    mutate(keypoint = str_remove(keypoint, "_Confidence"))

  ##### Create plot #####

  df %>%
    ggplot(aes(x = keypoint, y = confidence_mean)) +
    geom_segment(aes(x = keypoint,
      xend = keypoint,
      y = 0,
      yend = confidence_mean),
      color = "gray80") +
    geom_point(color = "gray40", size = 3) +
    theme_light() +
    coord_flip() +
    theme(
      panel.grid.major.y = element_blank(),
      panel.border = element_blank(),
      axis.ticks.y = element_blank()
    ) +
    labs(title = name) +
    ylab("mean confidence value") +
    xlab("") +
    ylim(0, 1000) +
    theme(plot.margin = margin(t = 0.5, r = 0, b = 0.5, l = 0, unit = "cm"))

  ##### Save Appendix 3 #####

  save_name <- str_c(name, "_a3.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 6,
    height = 8
  )
}

df$df_list_confidence %>%
  map2(df$name, appendix_threes)


###********************************************************** ###
##### FIGURE A4s: Mean OpenPose confidence value over frames #####
###********************************************************** ###

print("Working on A4s!")

### Helper Functions ###

plot_tot_conf <- function(df, first_frame) { ##### Create confidence over frames

  ##### Prepare Data #####
  df <- df %>%
    summarize(
      frame = frame,
      pid = pid,
      confidence_mean = rowMeans(across(contains("Confidence")), na.rm = TRUE)
    ) %>%
    ungroup()

  ##### Create Plot #####
  df %>%
    ggplot(aes(frame, confidence_mean)) +
    theme_light() +
    theme(text = element_text(size = 15)) +
    geom_smooth(se = FALSE, color = "gray40") +
    labs(
      y = "Mean confidence value (0-1000)",
      x = ""
    ) +
    xlim(first_frame, NA) +
    ggtitle("Mean confidence value over frames")
}


plot_bypid_conf <- function(df, first_frame) { ##### Create confidence over frames by person

  ##### Prepare Data #####
  df <- df %>%
    group_by(pid) %>%
    summarize(
      frame = frame,
      pid = pid,
      confidence_mean = rowMeans(across(contains("Confidence")), na.rm = TRUE)
    ) %>%
    ungroup()

  ##### Create Plot #####
  df %>%
    ggplot(aes(frame, confidence_mean, color = pid)) +
    theme_light() +
    geom_smooth(se = FALSE) +
    theme(
      text = element_text(size = 15),
      legend.title = element_blank(),
      legend.position = c(0.05, 0.15),
      legend.justification = c(0, 0),
      legend.background = element_rect(colour = "grey80"),
      legend.title.align = .5
    ) +
    labs(
      y = "Mean confidence value (0-1000)",
      x = ""
    ) +
    xlim(first_frame, NA) +
    ggtitle("Mean confidence value over frames (by person)") +
    scale_color_discrete(labels = c("Person 1", "Person 2"))
}


appendix_fours <- function(df, name, first_frame) {
  confidence_by_frame_plot <- plot_tot_conf(df, first_frame)
  confidence_by_frame_pid_plot <- plot_bypid_conf(df, first_frame)

  ##### Combine Plots #####
  plot_grid(
    plotlist = list(
      confidence_by_frame_plot,
      confidence_by_frame_pid_plot
    ),
    ncol = 1
  )

  ##### Save appendix 4 #####
  save_name <- str_c(name, "_a4.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 6,
    height = 8
  )
}


pmap(list(df$df_list_confidence, df$name, df$first_frame), appendix_fours)


###***************************************************** ###
##### FIGURE A5s: Total misclassification by keypoint ######
###***************************************************** ###

print("Working on FA5s!")

appendix_fives <- function(df, name) {

  ##### Prepare Data #####

  df <- df %>%
    pivot_longer(-c(frame, pid),
      names_to = "keypoint",
      values_to = "misclassifications"
    ) %>%
    select(frame, keypoint, misclassifications) %>%
    group_by(keypoint) %>%
    summarize(misclass_sum = sum(misclassifications, na.rm = TRUE)) %>%
    arrange(desc(misclass_sum))

  ##### Create plot #####

  df %>%
    ggplot(aes(x = keypoint, y = misclass_sum)) +
    geom_segment(aes(x = keypoint,
                    xend = keypoint,
                    y = 0,
                    yend = misclass_sum),
      color = "gray80"
    ) +
    geom_point(color = "gray40", size = 3) +
    theme_light() +
    coord_flip() +
    theme(
      panel.grid.major.y = element_blank(),
      panel.border = element_blank(),
      axis.ticks.y = element_blank()
    ) +
    labs(title = name) +
    ylab("sum of misclassifications") +
    xlab("") +
    theme(plot.margin = margin(t = 0.5, r = 0, b = 0.5, l = 0, unit = "cm"))

  ##### Save Appendix 5 #####

  save_name <- str_c(name, "_a5.pdf")

  ggsave(save_name,
    device = "pdf",
    path = path_output,
    width = 6,
    height = 8
  )
}

df$df_list_misclassifications %>%
  map2(df$name, appendix_fives)

print("All done! Finished producing all files up to appendix 5s.")