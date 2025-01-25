https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=pypi&page=dataset&inv=1&invt=AbmgWQ&project=prototype-pollution-fun&ws=!1m10!1m4!4m3!1sbigquery-public-data!2spypi!3sfile_downloads!1m4!1m3!1sprototype-pollution-fun!2sbquxjob_16f09557_19452329121!3sUS

```
SELECT 
  file.project AS project_name, 
  COUNT(*) AS num_downloads
FROM 
  `bigquery-public-data.pypi.file_downloads`
WHERE 
  DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY) AND CURRENT_DATE()
GROUP BY 
  file.project
HAVING 
  num_downloads > 10000
ORDER BY 
  num_downloads DESC;
```