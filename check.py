import os
import requests
import socket
import time
import datetime
import sys
import re
from alive_progress import alive_bar
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

# 파일 경로 설정
list_path = "C:\\list.txt"

# 대기 시간 설정
wait_time = 5

# 시작 시간 기록
start_time = datetime.datetime.now()

# 파일 존재 여부 확인
if not os.path.exists(list_path):
    print("파일이 존재하지 않습니다. 프로그램을 종료합니다.")
    sys.exit(1)

# 결과 저장을 위한 파일 열기
output_file = "result2.txt"
output_stream = open(output_file, "w")

# 도메인 상태별 카운트 초기화
up_count = 0
reset_count = 0
not_resolved_count = 0
connection_refused_count = 0
timeout_count = 0
warning_count = 0
nodomain_count = 0
ssl_protocol_count = 0
chromedriver_connect_count = 0
selenium_timeout_count = 0
error_count = 0

# URL 리스트 읽기
with open(list_path, "r") as f:
    url_list = f.readlines()

# Selenium 설정
options = Options()
options.headless = True
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--ignore-certificate-errors")
driver_path = "./chromedriver.exe"

def get_cdn_provider(headers):
    cdn_provider = "Unknown"

    if "cf-ray" in headers:
        cdn_provider = "Cloudflare"
    elif "x-cdn" in headers and headers["x-cdn"].lower() == "cloudbric":
        cdn_provider = "Cloudbric"
    elif "x-amz-cf-id" in headers or "x-cache" in headers and headers["x-cache"].lower().startswith("cloudfront"):
        cdn_provider = "Cloudfront"
    elif "x-akamai-request-id" in headers or "x-akamai-request-id" in headers:
        cdn_provider = "Akamai"
    # 추가적인 CDN 제공업체를 확인하려면 여기에 조건문을 추가하세요.

    return cdn_provider


def check_url(url, options=None):
    # URL 접속
    if not url.startswith("http"):
        url = "http://" + url
    
    for i in range(2): # 최대 2번 재시도
        try:
            response = requests.get(url, timeout=wait_time)
            headers = response.headers
            cdn_provider = get_cdn_provider(headers)


            driver = webdriver.Chrome(executable_path=driver_path, options=options)
            driver.get(url)
            time.sleep(wait_time)
            if "404" in driver.title or "Page Not Found" in driver.page_source:
                print(f"{url}: Page Not Found")
                status = "RESET"
            else:
                # 현재 URL 확인
                current_url = driver.current_url
                if "warning.or.kr" in current_url or "www.warning.or.kr" in current_url:
                    print(f"{current_url}: WARNING")
                    status = "WARNING"
                else:
                    print(f"{url}: UP")
                    status = "UP"

            # 캡쳐 저장
            capture_folder = './capture'
            if not os.path.exists(capture_folder):
                os.makedirs(capture_folder)
            capture_path = os.path.join(capture_folder, f"{url.split('//')[-1].split('/')[0]}.png")
            time.sleep(wait_time)  # 로딩 완료 대기
            capture_success = driver.get_screenshot_as_file(capture_path)  # 캡쳐 성공 여부를 확인합니다.

            driver.quit()
            break  # 성공했으므로 for 루프를 빠져나감

        except (socket.gaierror, socket.timeout) as ex:
            print(f"{url}: {str(ex)}")
            status = "RESET"
            if i < 1: # 최대 1번 재시도
                print(f"Retry: {i+1}/2")
                continue # 다시 시도

        except WebDriverException as ex:
            if "ERR_CONNECTION_RESET" in str(ex):
                print(f"{url}: RESET")
                status = "RESET"
            elif "ERR_NAME_NOT_RESOLVED" in str(ex):
                print(f"{url}: NOT_RESOLVED")
                status = "RESET"
            elif "ERR_CONNECTION_REFUSED" in str(ex):
                print(f"{url}: CONNECTION_REFUSED")
                status = "CONNECTION_REFUSED"
            elif "ERR_CONNECTION_TIMED_OUT" in str(ex):
                if i < 2:  # 최대 2번 재시도
                    print(f"Retry: {i+1}/3")
                    continue  # 다시 시도
                else:
                    print(f"{url}: TIMEOUT")
                    status = "TIMEOUT"
                    break  # for 루프를 빠져나감
            elif "DNS_PROBE_FINISHED_NXDOMAIN" in str(ex):
                print(f"{url}: NXDOMAIN")
                status = "NODOMAIN"
            elif "ERR_SSL_PROTOCOL_ERROR" in str(ex):
                print(f"{url}: SSL_PROTOCOL")
                status = "SSL_PROTOCOL"
            elif "warning.or.kr" in url or "www.warning.or.kr" in url:
                print(f"{url}: WARNING")
                status = "WARNING"
                # 캡쳐 저장
                capture_folder = './capture'
                if not os.path.exists(capture_folder):
                    os.makedirs(capture_folder)
                capture_path = os.path.join(capture_folder, f"{url.split('//')[-1].split('/')[0]}.png")
                time.sleep(wait_time)  # 로딩 완료 대기
                driver.get_screenshot_as_file(capture_path)
            elif "ERR_SELENIUM_TIMEOUT" in str(ex): # selenium timeout 오류
                print(f"{url}: ERR_SELENIUM_TIMEOUT")
                status = "ERR_SELENIUM_TIMEOUT"
                # 캡쳐 저장
                capture_folder = './capture'
                if not os.path.exists(capture_folder):
                    os.makedirs(capture_folder)
                capture_path = os.path.join(capture_folder, f"{url.split('//')[-1].split('/')[0]}.png")
                driver.get_screenshot_as_file(capture_path)
                break # for 루프를 빠져나감
            elif "ERR_CHROMEDRIVER_CONNECT" in str(ex): # chromedriver 연결 오류
                print(f"{url}: ERR_CHROMEDRIVER_CONNECT")
                status = "RESET"
                if i < 1: # 최대 1번 재시도
                    print(f"Retry: {i+1}/2")
                    continue # 다시 시도
                else:
                    status = "ERR_CHROMEDRIVER_CONNECT"
                    break # for 루프를 빠져나감
            else:
                print(f"{url}: ERROR({str(ex)})")
                status = f"ERROR({str(ex)})"
            break # 성공했으므로 for 루프를 빠져나감


    # 결과값 저장
    try:
        ip = socket.gethostbyname(url.split('//')[-1].split('/')[0])
    except:
        ip = "N/A"

    check_time = datetime.datetime.now()
    domain_status_list.append((url, ip, status, check_time, cdn_provider))
    
    # 결과값 반환
    return (url, ip, status, datetime.datetime.now(), cdn_provider)


# URL별로 상태 확인
results = []
domain_status_list = []
with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
    futures = {executor.submit(check_url, url.strip(), options): url for url in url_list}

    # 모든 작업이 완료될 때까지 대기하며 progress bar 출력
    with alive_bar(len(futures)) as bar:
        for future in concurrent.futures.as_completed(futures):
            bar()
            domain_status = future.result()
            domain_status_list.append(domain_status)

# 도메인별 결과값 저장
results = []
for domain, ip, status, check_time, cdn_provider in domain_status_list:
    result = f"{domain}, {ip}, {status}, {check_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}, {cdn_provider}"
    results.append(result)
    output_stream.write(result + "\n")


#도메인 상태별 수와 비율 출력
total_count = len(domain_status_list)
up_count = len([d for d in domain_status_list if d[2] == "UP"])
reset_count = len([d for d in domain_status_list if d[2] == "RESET"])
not_resolved_count = len([d for d in domain_status_list if d[2] == "NOT_RESOLVED"])
connection_refused_count = len([d for d in domain_status_list if d[2] == "CONNECTION_REFUSED"])
timeout_count = len([d for d in domain_status_list if d[2] == "TIMEOUT"])
warning_count = len([d for d in domain_status_list if d[2] == "WARNING"])
nodomain_count = len([d for d in domain_status_list if d[2] == "NODOMAIN"])
ssl_protocol_count = len([d for d in domain_status_list if d[2] == "SSL_PROTOCOL"])
chromedriver_connect_count = len([d for d in domain_status_list if d[2] == "ERR_CHROMEDRIVER_CONNECT"])
selenium_timeout_count = len([d for d in domain_status_list if d[2] == "ERR_SELENIUM_TIMEOUT"])
error_count = len([d for d in domain_status_list if "ERROR" in d[2]])
up_ratio = up_count / total_count * 100 if total_count else 0
down_ratio = (reset_count + not_resolved_count + connection_refused_count + timeout_count + warning_count + nodomain_count + ssl_protocol_count + chromedriver_connect_count + selenium_timeout_count + error_count) / total_count * 100 if total_count else 0

#결과 출력
output_stream.write(f"\nTotal domains: {total_count} / ")
output_stream.write(f"UP domains: {up_count}, Ratio: {up_ratio:.2f}% / ")
output_stream.write(f"DOWN domains: {reset_count + not_resolved_count + connection_refused_count + timeout_count + warning_count + nodomain_count + ssl_protocol_count + chromedriver_connect_count + selenium_timeout_count + error_count}, Ratio: {down_ratio:.2f}% / ")
output_stream.write(f"Execution time: {(datetime.datetime.now() - start_time).total_seconds():.0f} seconds\n")

#결과 저장 파일 닫기
output_stream.close()

print("결과가 성공적으로 저장되었습니다.")