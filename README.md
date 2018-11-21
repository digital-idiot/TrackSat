# TrackSat

Purely Python based Satellite Tracking Tool

Track all the satellites specified in [CelesTrak](https://www.celestrak.com/NORAD/elements/master.asp)

Webapp: https://github.com/digital-idiot/TrackSat-Web

Conference Paper: https://doi.org/10.5194/isprs-annals-IV-5-109-2018

##Abstract

Accurate monitoring of satellites plays a pivotal role in analysing critical mission specific parameters for estimating orbital position uncertainties. An appropriate database management system (DBMS) at the software end, could prove its potential as a convenient solution over the existing file based two line element (TLE) data structure. The current web-based satellite tracking systems, such as n2yo, satview, and satflare, are unable to provide location-based satellite monitoring. Moreover, the users need to zoom into the displayed world map for obtaining information of the satellites that are currently over the respective area. Also, satellite searching is a cumbersome task in these web-based systems. In this research work, a systematic approach has been utilised to develop a generic open-source Web-GIS based tool for addressing the aforementioned issues. This tool incorporates a PostgreSQL database for storing the parsed TLE data which are freely available on the CelesTrak (NORAD) repository. Our choice of selecting PostgreSQL as a backend DB is primarily due to its open source and scalable properties compared to other resource intensive databases. Using suitable python libraries (e.g. Skyfield and Orbit-Predictor), the position and velocity at any point of time can be accurately estimated. For this purpose, the tool has been tested on several cities for displaying location-based satellite tracking that includes different types of space-objects. 
