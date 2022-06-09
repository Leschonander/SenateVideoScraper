library(tidyverse)

masterfile <- read_csv("./SenateVideoFiles/MasterFile.csv")
basic_tags <- read_csv("basic_tags_tibble.csv") %>% .[[1]]

masterfile_with_tags <- masterfile %>%
  mutate(
    Tags = str_extract_all(Title, paste(basic_tags, collapse = "|")),
    Tags = map_chr(Tags, toString),
    Tags = gsub("\\b", '"', Tags, perl=T),
    Tags = map_chr(Tags, ~ str_c("[", .x, "]"))
    )

masterfile_with_tags %>%
  write_csv("MasterFileWithTags.csv")

print("Tags added")