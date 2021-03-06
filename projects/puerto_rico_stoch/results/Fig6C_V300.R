library("ggplot2")
library(dplyr)
library(gridExtra)
library(RColorBrewer)

dir_plots = "C:\\Users\\benne\\PycharmProjects\\temoatools\\projects\\puerto_rico_stoch\\results"

#===================================================================
# All technologies (no cases)
#===================================================================

# Set directory
setwd(dir_plots)

# Load data:
df1 <- read.csv("activity_by_fuel_toPlot.csv")
df2 <- read.csv("activity_by_tech_toPlot.csv")
df3 <- read.csv("activity_by_tech_toPlot.csv")

#----------------
# Process data
#----------------

# Remove scenarios that do not use all technologies
df1<-df1[(df1$Scenario=="All"),]
df2<-df2[(df2$Scenario=="All"),]
df3<-df3[(df3$Scenario=="All"),]

# Remove 'No IRP'
# df1<-df1[!(df1$carbon_tax=='No IRP') ,]
# df2<-df2[!(df2$carbon_tax=='No IRP') ,]
# df3<-df3[!(df3$carbon_tax=='No IRP') ,]

# Remove "solve" scenario (scenario run without stochastics)
df1<-df1[!(df1$s=="solve"),]
df2<-df2[!(df2$s=="solve"),]
df3<-df3[!(df3$s=="solve"),]

# Rename years
rename <- c("2016"="2016-20",
            "2021"="2021-25",
            '2026'="2026-30",
            '2031'="2031-35",
            '2036'="2036-40")
df1 <- transform(df1, Year = rename[as.character(Year)])
df2 <- transform(df2, Year = rename[as.character(Year)])
df3 <- transform(df3, Year = rename[as.character(Year)])

# Rename prob_type
rename <- c("None"="'None'",
            "Historical"="'Historical storm frequency'",
            "Climate Change"="'Increased storm frequency'")
df1 <- transform(df1, prob_type = rename[as.character(prob_type)])
df2 <- transform(df2, prob_type = rename[as.character(prob_type)])
df3 <- transform(df3, prob_type = rename[as.character(prob_type)])

# Rename carbon_tax
rename <- c("No IRP"="'No RPS'",
            "IRP"="'RPS'",
            "Tax"="'US$'~100~t^-1~CO[2]")
df1 <- transform(df1, carbon_tax = rename[as.character(carbon_tax)])
df2 <- transform(df2, carbon_tax = rename[as.character(carbon_tax)])
df3 <- transform(df3, carbon_tax = rename[as.character(carbon_tax)])

# Rename Type column
names(df1)[names(df1) == 'Type'] <- 'Technology'
names(df2)[names(df2) == 'Type'] <- 'Technology'
names(df3)[names(df3) == 'Type'] <- 'Technology'

# Rename Technology - df1
rename <- c("ELC_CENTRAL"="exclude",
            "ELC_DIST"="exclude",
            "BIO"="exclude",
            "COAL_TAXED"="'Coal + petroleum'",
            "DSL_TAXED"="'Coal + petroleum'",
            "HYDRO"="exclude",
            "MSW_LF_TAXED"="exclude",
            'NATGAS_TAXED'="'Natural gas'",
            'OIL_TAXED'="'Coal + petroleum'",
            "SOLAR"="'Solar'",
            "WIND"="'Wind'")
df1 <- transform(df1, Technology = rename[as.character(Technology)])

# Rename Technology - df2
rename <- c("DIST_COND"="'Distribution - overhead'",
            "DIST_TWR"="exclude",
            "DSL_TAX"="exclude",
            "EC_BATT"="exclude",
            "EC_BIO"="exclude",
            "EC_COAL"="exclude",
            "EC_DSL_CC"="exclude",
            "EC_NG_CC"="exclude",
            "EC_NG_OC"="exclude",
            "EC_OIL_CC"="exclude",
            "EC_SOLPV"="exclude",
            "EC_WIND"="exclude",
            "ED_BATT"="exclude",
            "ED_BIO"="exclude",
            "ED_NG_CC"="exclude",
            "ED_NG_OC"="exclude",
            "ED_SOLPV"="exclude",
            "ED_WIND"="exclude",
            "EX_COAL"="exclude",
            "EX_DSL_CC"="exclude",
            "EX_DSL_SIMP"="exclude",
            "EX_HYDRO"="exclude",
            "EX_MSW_LF"="exclude",
            "EX_NG_CC"="exclude",
            "EX_OIL_TYPE1"="exclude",
            "EX_OIL_TYPE2"="exclude",
            "EX_OIL_TYPE3"="exclude",
            "EX_SOLPV"="exclude",
            "EX_WIND"="exclude",
            "IMPBIO"="exclude",
            "IMPCOAL"="exclude",
            "IMPDSL"="exclude",
            "IMPHYDRO"="exclude",
            "IMPMSW_LF"="exclude",
            "IMPNATGAS"="exclude",
            "IMPOIL"="exclude",
            "IMPSOLAR"="exclude",
            "IMPWIND"="exclude",
            "LOCAL"="exclude",
            "MSW_LF_TAX"="exclude",
            "NATGAS_TAX"="exclude",
            "OIL_TAX"="exclude",
            "SUB"="exclude",
            "TRANS"="'Transmission - overhead'",
            "UGND_DIST"="'Distribution - buried'",
            "UGND_TRANS"="'Transmission - buried'")
df2 <- transform(df2, Technology = rename[as.character(Technology)])

# Rename Technology - df3
rename <- c("EX_COAL"="'Centralised - fossil'",
            "EX_DSL_CC"="'Centralised - fossil'",
            "EX_DSL_SIMP"="'Centralised - fossil'",
            "EX_NG_CC"="'Centralised - fossil'",
            "EX_OIL_TYPE1"="'Centralised - fossil'",
            "EX_OIL_TYPE2"="'Centralised - fossil'",
            "EX_OIL_TYPE3"="'Centralised - fossil'",
            "EC_COAL"="'Centralised - fossil'",
            "EC_DSL_CC"="'Centralised - fossil'",
            "EC_NG_CC"="'Centralised - fossil'",
            "EC_NG_OC"="'Centralised - fossil'",
            "EC_OIL_CC"="'Centralised - fossil'",
            "ED_NG_CC"="'Distributed - fossil'",
            "ED_NG_OC"="'Distributed - fossil'",
            "EX_HYDRO"="'Centralised - renewable'",
            "EX_MSW_LF"="'Centralised - renewable'",
            "EX_SOLPV"="'Centralised - renewable'",
            "EX_WIND"="'Centralised - renewable'",
            "EC_BIO"="'Centralised - renewable'",
            "EC_SOLPV"="'Centralised - renewable'",
            "EC_WIND"="'Centralised - renewable'",
            "ED_BIO"="'Distributed - renewable'",
            "ED_SOLPV"="'Distributed - renewable'",
            "ED_WIND"="'Distributed - renewable'",
            "EC_BATT"="exclude",
            "ED_BATT"="exclude",
            "DIST_COND"="exclude",
            "DIST_TWR"="exclude",
            "DSL_TAX"="exclude",
            "IMPBIO"="exclude",
            "IMPCOAL"="exclude",
            "IMPDSL"="exclude",
            "IMPHYDRO"="exclude",
            "IMPMSW_LF"="exclude",
            "IMPNATGAS"="exclude",
            "IMPOIL"="exclude",
            "IMPSOLAR"="exclude",
            "IMPWIND"="exclude",
            "LOCAL"="exclude",
            "MSW_LF_TAX"="exclude",
            "NATGAS_TAX"="exclude",
            "OIL_TAX"="exclude",
            "SUB"="exclude",
            "TRANS"="exclude",
            "UGND_DIST"="exclude",
            "UGND_TRANS"="exclude")
df3 <- transform(df3, Technology = rename[as.character(Technology)])


# Slice dataframes to keep technologies of interest
df1 <- df1[ which(df1$Technology !='exclude'),]
df2 <- df2[ which(df2$Technology !='exclude'),]
df3 <- df3[ which(df3$Technology !='exclude'),]

# Combine same technologies within each scenario (s)
groupings = c("Scenario","s","Technology","Year","case","prob_type","infra",
              "carbon_tax","infra_and_carbon_tax", "entry")
df1_smry <- df1 %>% 
  group_by(.dots=groupings)%>%
  summarise(Value=sum(Value))
df2_smry <- df2 %>% 
  group_by(.dots=groupings)%>%
  summarise(Value=sum(Value))
df3_smry <- df3 %>% 
  group_by(.dots=groupings)%>%
  summarise(Value=sum(Value))


df1_smry$Analysis <- "'Fuel use'"
df2_smry$Analysis <- "'Transmission and distribution'"
df3_smry$Analysis <- "'Grid architecture'"

# Combine dataframes
df <- rbind(df1_smry, df2_smry, df3_smry)

# Rename case
names(df)[names(df) == 'case'] <- 'Case'
rename <- c("None-All-No IRP"="'No policy - No storms'",
            "None-All-IRP"="'RPS - No storms'",
            "None-All-Tax"="'US$'~100~t^-1~CO[2]'- No storms'",
            "Historical-All-No IRP"="'No policy - Historical storm frequency'",
            "Historical-All-IRP"="'RPS - Historical storm frequency'",
            "Historical-All-Tax"="'US$'~100~t^-1~CO[2]'- Historical storm frequency'",
            "Climate Change-All-No IRP"="'No policy - Increased storm frequency'",
            "Climate Change-All-IRP"="'RPS - Increased storm frequency'",
            "Climate Change-All-Tax"="'US$'~100~t^-1~CO[2]' - Increased storm frequency'")
df <- transform(df, Case = rename[as.character(Case)])

# Change subplot order - Case
levels <- c("'No policy - No storms'",
            "'No policy - Historical storm frequency'",
            "'No policy - Increased storm frequency'",
            "'RPS - No storms'",
            "'RPS - Historical storm frequency'",
            "'RPS - Increased storm frequency'",
            "'US$'~100~t^-1~CO[2]'- No storms'",
            "'US$'~100~t^-1~CO[2]'- Historical storm frequency'",
            "'US$'~100~t^-1~CO[2]' - Increased storm frequency'")
df$Case <- factor(df$Case, levels = levels)

# Change subplot order - prob_type
levels <- c("'No storms'","'Historical storm frequency'","'Increased storm frequency'")
df$prob_type <- factor(df$prob_type, levels = levels)

# Change subplot order - carbon_tax
levels <- c("'No RPS'","'RPS'","'New RPS'")
df$carbon_tax <- factor(df$carbon_tax, levels = levels)

# Change subplot order - Technology
levels <- c("'Coal + petroleum'","'Natural gas'","'Solar'","'Wind'",
            "'Transmission - overhead'","'Transmission - buried'",
            "'Distribution - overhead'","'Distribution - buried'",
            "'Centralised - fossil'","'Centralised - renewable'",
            "'Distributed - fossil'","'Distributed - renewable'")
df$Technology <- factor(df$Technology, levels = levels)



# Summarise to create line plots
df_smry <- df %>% # the names of the new data frame and the data frame to be summarised
  group_by(.dots=c("Technology","Case", "Year", "Analysis")) %>%   # the grouping variable
  summarise(mean = mean(Value),  # calculates the mean
            min = min(Value), # calculates the minimum
            max = max(Value),# calculates the maximum
            sd=sd(Value)) # calculates the standard deviation


# The palette with black: http://www.cookbook-r.com/Graphs/Colors_(ggplot2)/
cbPalette <- c( "#E69F00", "#56B4E9", "#009E73", "#D55E00", "#CC79A7", "#0072B2")
cbPalette <- c(  
  "#999999", 
  "#000000", 
  "#56B4E9", 
  "#0072B2", 
  "#E69F00", 
  "#D55E00" )


# black #000000
# orange #E69F00
# blue ##56B4E9
# green #009E73
# yellow #F0E442
# dark blue #0072B2
# red #D55E00
# purple #CC79A7

cbPalette <- c(brewer.pal(9,'Spectral'))

# cbPalette <- c(brewer.pal(3,'Greys'),brewer.pal(3,'Greens'),brewer.pal(3,'Blues'))

# cbPalette <-c('#cccccc','#969696','#525252',
# '#bdd7e7','#6baed6','#2171b5',
# '#fcae91','#fb6a4a','#cb181d')


cbPalette <-c('#252525','#636363','#969696',
'#bdd7e7','#6baed6','#2171b5',
'#fcae91','#fb6a4a','#cb181d')

# cbPalette <-c('#252525', '#6baed6', '#fb6a4a', 
              # '#31a354', '#3182bd', '#de2d26',
              # '#006d2c','#08519c', '#a50f15')

cbPalette <-c('#252525',  '#31a354', '#006d2c',
              '#6baed6', '#3182bd', '#08519c',
              '#fb6a4a', '#de2d26','#a50f15')


#==============================
# Shaded line plots
# Helpful resources:
# https://ggplot2.tidyverse.org/reference/geom_ribbon.html
# https://kohske.wordpress.com/2010/12/27/faq-geom_line-doesnt-draw-lines/
#==============================
dodge = 0.2
ggplot(df_smry,aes(x=Year, y=mean, ymin=min, ymax=max, fill=Case, group=Case, color=Case))+
  facet_wrap(~Analysis+Technology, labeller = label_parsed)+
  geom_line(size=1,position=position_dodge(width=dodge))+
  geom_ribbon(alpha=0.2, colour = NA,position=position_dodge(width=dodge))+
  geom_point(position=position_dodge(width=dodge))+
  scale_color_manual(values=cbPalette, labels=expression('No policy - No storms',
                                                         'No policy - Historical storm frequency',
                                                         'No policy - Increased storm frequency',
                                                         'RPS - No storms',
                                                         'RPS - Historical storm frequency',
                                                         'RPS - Increased storm frequency',
                                                         'US$'~100~t^-1~CO[2]~'- No storms',
                                                         'US$'~100~t^-1~CO[2]~'- Historical storm frequency',
                                                         'US$'~100~t^-1~CO[2]~' - Increased storm frequency'),guide = guide_legend(nrow = 3, label.hjust = 0))+
  scale_fill_manual(values=cbPalette, labels=expression('No policy - No storms',
                                                        'No policy - Historical storm frequency',
                                                        'No policy - Increased storm frequency',
                                                        'RPS - No storms',
                                                        'RPS - Historical storm frequency',
                                                        'RPS - Increased storm frequency',
                                                        'US$'~100~t^-1~CO[2]~'- No storms',
                                                        'US$'~100~t^-1~CO[2]~'- Historical storm frequency',
                                                        'US$'~100~t^-1~CO[2]~' - Increased storm frequency'),guide = guide_legend(nrow = 3, label.hjust = 0))+
  labs(x='Year', y=expression(paste("Activity (TWh y"^-1,")")))+
  theme(legend.position="bottom", legend.title = element_blank(),axis.text.x = element_text(angle = 90,vjust=0.5))
  


# Save
ggsave('Fig6C_V300.png', device="png",
       width=8.0, height=8.0, units="in",dpi=1000)
