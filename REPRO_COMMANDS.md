# Exact commands used on 2026-10-01 (reproduction cookbook)

These are the commands from the 01/10 session, taken from the transcript and cleaned of temporary paths.

- **Shells.** Git Bash on the lab PC (Windows 11, Ryzen 7 7800X3D).
  - `py -3.12` is the system Python. There is no `python3` on this PC.
  - The lab venv is `C:\Users\RESEARCHER\Desktop\c2_experimental\.venv`.
- **Read-only checks.** These were run by Claude.
- **Changes.** Every command that creates or changes something is marked **[WRITE]**. Who ran each one is noted.

## A. Import the results of the old AWS run (54 slices, 29-30/09) into the lab
```
cd /c/home/researcher/Desktop/c2_experimental/aws_repo
py -3.12 monitor_git.py --once --fetch          # old monitor: copies results of every run/* branch into resultats/<branch>/results
cd ..
.venv/Scripts/python.exe scripts/cloud/import_results.py c2_cloud_run aws_repo/resultats/*/results
#   -> imported 399, duplicates 0, refused 0 (engine sha checked per result)
.venv/Scripts/python.exe scripts/stream_finish.py
#   -> newly excluded [61]; tracker 94 excluded / 61 open / 1 partial
py -3.12 q/tools/routec_progress.py             # (from aws_repo) read-only: finished jobs per old run branch
```
The rehearsal job 028:0:8 (CI, branch `run/qci-a`) was imported the same way: `python q/monitor_q.py --fetch` was run with
`Q_QUEUE=queue-ci Q_RUNPREFIX=run/qci-` and the output dir was `resultats_ci/` (a local copy, not tracked).

## B. Build the queues [WRITE: Claude, on this GitHub repo only]
```
cd /c/home/researcher/Desktop/c2_experimental/aws_repo
py -3.12 q/make_queue.py --branch queue --cap 115 --campaign c2q-20261001
#   -> 3026 jobs, first 062:0:15, last 003:12:13; control {"mode":"run","cap_usd":115.0,"lease_s":1800,"ratio":1.3,"max_fail":2}
py -3.12 q/make_queue.py --branch queue-ci --cap 1000 --campaign c2q-ci --jobs 028:0:8,028:1:8,028:2:8,028:3:8,028:4:8,028:5:8,028:6:8,028:7:8
```
`make_queue.py` refuses to overwrite a queue that already holds events unless `--force` is given. **Never use `--force` on
`queue` while machines run.**

## C. AWS (account 957809771373)
```
aws login --region eu-north-1                                     # browser login (the user)
aws sts get-caller-identity --region eu-north-1 --query "{account:Account,arn:Arn}" --output text

# Spot vCPU quota (L-34B43A08 = "All Standard (A,C,D,H,I,M,R,T,Z) Spot Instance Requests") and pending requests
for R in eu-north-1 us-east-2 us-east-1 us-west-2 eu-west-2 eu-central-1 eu-west-1 ap-northeast-1; do
  echo "== $R"
  aws service-quotas get-service-quota --service-code ec2 --quota-code L-34B43A08 --region $R --query "Quota.Value" --output text
  aws service-quotas list-requested-service-quota-change-history --service-code ec2 --region $R \
     --query "RequestedQuotas[].[QuotaCode,DesiredValue,Status,Created]" --output text
done

# 7-day spot price range of c7a.8xlarge
for R in eu-north-1 us-east-2 us-east-1 us-west-2; do printf "%-12s " $R
  aws ec2 describe-spot-price-history --region $R --instance-types c7a.8xlarge --product-descriptions "Linux/UNIX" \
     --start-time "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S)" --query "SpotPriceHistory[].SpotPrice" --output text \
   | tr '\t' '\n' | sort -n | awk 'NR==1{m=$1}{a[NR]=$1}END{printf "min %s median %s max %s (n=%d)\n",m,a[int(NR/2)+1],a[NR],NR}'
done
```
**[WRITE: Claude, on the user's explicit request]** the AWS budget `c2-route-c-backstop`. It sends alerts only and does not stop anything.

`budget.json`:
```
{"BudgetName":"c2-route-c-backstop","BudgetLimit":{"Amount":"120","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST",
 "CostTypes":{"IncludeTax":true,"IncludeSubscription":true,"UseBlended":false,"IncludeRefund":false,"IncludeCredit":false,
              "IncludeUpfront":true,"IncludeRecurring":true,"IncludeOtherSubscription":true,"IncludeSupport":true,
              "IncludeDiscount":true,"UseAmortized":false}}
```
`notif.json`: one entry per threshold 50, 80, 95 and 100, each of the form
`{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":T,"ThresholdType":"PERCENTAGE"},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"206353265+amazing-source@users.noreply.github.com"}]}`.

```
aws budgets create-budget --account-id 957809771373 --budget file://budget.json --notifications-with-subscribers file://notif.json
aws budgets describe-budgets --account-id 957809771373 --query "Budgets[].[BudgetName,BudgetLimit.Amount]" --output text
```

## D. Azure (subscription 8f9f28ce-19bb-46f4-8a28-106315fc685e)
In Git Bash, put `MSYS_NO_PATHCONV=1` before any az command that takes a `/subscriptions/...` argument. Without it, Git Bash rewrites
the path and az answers "MissingSubscription".
```
az login --output none; az account list -o table                 # the user picks the account in the browser
SUB=$(az account show --query id -o tsv)
az rest --method get --url "https://management.azure.com/subscriptions/$SUB?api-version=2022-12-01" \
   --query "{state:state,quotaId:subscriptionPolicies.quotaId,spendingLimit:subscriptionPolicies.spendingLimit}"
#   -> Enabled, PayAsYouGo_2014-09-01, Off

for P in Microsoft.Compute Microsoft.Network Microsoft.Quota; do az provider register -n $P --wait; done   # [WRITE: Claude, free]

# quotas: "lowPriorityCores" = Total Regional Low-priority (Spot) vCPUs; "cores" = Total Regional vCPUs
az vm list-usage --location eastus -o json | py -3.12 -c "import json,sys;[print(u['name']['value'],u['currentValue'],u['limit']) for u in json.load(sys.stdin) if u['name']['value'] in ('lowPriorityCores','cores') or 'HB' in u['name']['localizedValue']]"
MSYS_NO_PATHCONV=1 az quota request list --scope "/subscriptions/$SUB/providers/Microsoft.Compute/locations/eastus" \
   --query "[].{state:properties.provisioningState,msg:properties.message}" -o json

# sizes allowed for this subscription (empty restriction = allowed)
az vm list-skus --location eastus --all --query "[?name=='Standard_HB120rs_v3'||name=='Standard_HB120rs_v2'||name=='Standard_HB176rs_v4'].{size:name,r:join(',',restrictions[].reasonCode)}" -o tsv

# spot retail price (no login needed)
curl -s -G "https://prices.azure.com/api/retail/prices" --data-urlencode \
  "\$filter=serviceName eq 'Virtual Machines' and armRegionName eq 'eastus' and armSkuName eq 'Standard_HB120rs_v3' and priceType eq 'Consumption'" \
 | py -3.12 -c "import json,sys;[print(i['meterName'],i['productName'],i['retailPrice']) for i in json.load(sys.stdin)['Items'] if 'Windows' not in i['productName']]"
```

**Portal path for a quota increase (French UI).**
1. Recherche « Quotas », puis « Calcul ».
2. Filter on the region (East US), then search « Low-priority » (the Spot quota is called « Total des processeurs virtuels de faible
   priorité régionaux »).
3. Click the pencil, then type the new limit.
4. If the automatic request fails ("0 of 477"), use « Créer une demande de support » (Quota, Calcul-VM, région, Spot, 480).
   - That is how ticket **2610010050004359** was opened on 01/10.

## E. PC run (lab)
```
powershell -ExecutionPolicy Bypass -File q\tools\start_pc_run.ps1        # 4 slots, CPUs 12-15, BelowNormal
# full speed (Git Bash):
cd /c/home/researcher/Desktop/c2_experimental && nohup .venv/Scripts/python.exe scripts/sched.py 12 > logs/sched_nohup.out 2>&1 &
nohup bash scripts/tracker_loop.sh > /dev/null 2>&1 &
# stop everything (PowerShell):
Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'c2_experimental' -and $_.Name -match 'python|bash' } | % { Stop-Process -Id $_.ProcessId -Force }
```
