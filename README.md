# package-dependency-networks
Supplementary material for MSR2017 paper Structure and Evolution of Package Dependency Networks

## Data files

 - cleaned_JS_dependency_final.csv - List all packages and their dependencies. For each package `(project_github, project_version, project_ver)` it specifies that it had a dependency `(adopted_name, adopted_ver)`.
   - `project_github` - github repository name. For published packages, it is the same as the project name
   - `project_name` - packag name
   - `commit_ts` - version release time or dependency file commit time (unix timestamp)
   - `project_ver` - release version
   - `adopted_name` - name of a an included package 
   - `adopted_ver` - version of the included package
   - `is_published` - is the package published (the one defined by project_name)
   - `new_ver` - If adopted_ver is semantic, what was the most recent version available during commit_ts
   
 - cleaned_JS_release_final.csv - Lists all packages and their release dates
   - `project_github`  - github repository name
   - `project_name` - project name 
   - `project_ver` - version
   - `release_ts` - release time 
   - `is_published` - is package published


## Samples

cleaned_JS_dependency_final.csv
```
project_github,project_name,commit_ts,project_ver,adopted_name,adopted_ver,is_published,new_ver
mimosa-jshint,mimosa-jshint,1392511522,1.1.1,jshint,2.4.3,1,2.4.3
mimosa-jshint,mimosa-jshint,1392511522,1.1.1,lodash,2.4.1,1,2.4.1
mimosa-jshint,mimosa-jshint,1392254925,1.1.0,jshint,2.3.0,1,2.3.0
mimosa-jshint,mimosa-jshint,1392254925,1.1.0,lodash,2.4.1,1,2.4.1
```


cleaned_JS_release_final.csv
```
project_github,project_name,project_ver,release_ts,is_published
mimosa-jshint,mimosa-jshint,1.1.1,1392511522,1
mimosa-jshint,mimosa-jshint,1.1.0,1392254925,1
mimosa-jshint,mimosa-jshint,1.1.3,1393967691,1
mimosa-jshint,mimosa-jshint,1.1.2,1393885960,1
```


