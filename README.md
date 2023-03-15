# 이 저장소는
현재 PC를 기준으로 도메인에 접속할 수 있는지 확인하는 코드입니다. 파이썬 코드이며, 출력값은 다음과 같습니다.

* 사이트 주소
* ip주소
* 사이트 상태

# 준비물
1. 크롬이 설치되어 있어야 합니다. 또한 설치된 크롬 버전에 맞추어 [Chromedriver](https://chromedriver.chromium.org/downloads)를 **파이썬 코드가 있는 폴더**에 다운로드 받아주세요.
2. 도메인 목록. 도메인 목록은 list.txt 파일에 한줄 씩 아래와 같이 입력해 주세요.

```
https://www.naver.com
https://www.gaonwiki.com
https://uiharu.gaon.xyz
```

list.txt 파일은 <code>C:\list.txt</code>에 위치할 수 있도록 해주세요.

# 결과값
결과값은 스크립트를 실행한 디렉토리에 <code>result.txt</code>로 저장되어 있습니다. 결과는 다음과 같은 형태로 나옵니다.

```
www.naver.com, 223.130.200.107, UP, AKAMAI, 2023-03-10 09:39:52.2994
www.gaonwiki.com, 104.21.82.129, UP, CLOUDFLARE, 2023-03-10 09:39:53.3378
uiharu.gaon.xyz, 129.154.210.92, UP, Unknown, 2023-03-10 09:39:53.4083
```

도메인, ip주소, 결과 코드, 확인 시간(연-월-일 시:분:초 밀리초) 형태로 결과가 나옵니다.

## 결과 코드 종류
### 정상 작동(UP)
정상적으로 작동하는 경우, UP이라고 표시됩니다.

### 정상 작동(UP)
정상적으로 작동하는 경우, UP이라고 표시됩니다.

### 연결 재설정(RESET)
연결이 재설정 되었다는 오류인 <code>ERR_CONNECTION_RESET</code>인 경우, RESET이라고 표시됩니다.

대부분 검열로 인해 저런 코드가 뜹니다. ~~히토미~~

### warning.or.kr로 이동(WARNING)
warning.or.kr 또는 www.warning.or.kr로 이동하는 경우, WARNING이라고 표시됩니다.

### 사이트가 존재하지 않는 경우(NODOMAIN)
사이트가 존재하지 않는다는 코드인 <code>DNS_PROBE_FINISHED_NXDOMAIN</code>인 경우, NODOMAIN이라고 표시됩니다.

### 기타 오류(ERROR)
기타 오류는 ERROR라 뜹니다.

# 주의사항
다음 주의사항을 꼼꼼히 읽어주세요!

## HTML 코드가 쉘 창에 뜹니다.
이건 어쩔 수가 없어요. 제 능력 밖 인 거 같아요.

## 인터넷에 연결되어 있어야 돼요.
당연하지만 인터넷에 연결되어 있어야 확인이 가능해요.

## list.txt 파일이 반드시 C드라이브 바로 밑에 있어야 해요.
그러지 않으면 작동하지 않아요.

# 속도
멀티스레드를 사용하고, 모든 스레드를 사용하기 때문에 스레드 수가 많고, 성능이 높으며, 네트워크 속도가 빠를 수록 속도가 빠릅니다.