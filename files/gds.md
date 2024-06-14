## GDS 변경사항

디스코드 봇을 통해 GDS 변경사항을 수신 받는 후 타 플러그인과 연동한다.   
현재는 비디오 변경사항을 받아서 PLEX MATE를 통한 스캔만 구현되어 있다.

메인서버의 아래 두 가지 파일처리를 자동 방송하며 GDS 관리자가 개별적으로 방송할 수도 있다.   
- 방송중 파일처리   
- S-Moive 게시판 파일처리   


여담으로 이 모든 것은 구버전에 있었던 Google Drive API - changes 사용으로 대체되어야 한다.   

----
<br>

## 방송하기

- 기본적으로 PLEX MATE - 스캔 - 설정 - 테스트 항목을 통한 실행과 같으며 모든 사용자들 PLEX에 영향을 준다.   
- /ROOT/GDRIVE - 으로 시작해야 함.
- 모드
    * 추가 : 폴더 추가, 폴더 안 영상 파일 추가. 
    * 파일 삭제 : 폴더 안 영상 파일 삭제.
    * 폴더 삭제 : 폴더 삭제.
    * 메타새로고침 : 컨텐츠 루트 폴더를 지정. 주로 자막파일 추가,삭제,교체시 사용
- API
    * URL : /gds_tool/api/fp/broadcast
    * PARAM 
        - gds_path : 경로. /ROOT/GDRIVE 으로 시작 (필수)  
        - scan_mode: 생략시 ADD (optional)   
        - apikey : apikey (필수) 

  ```python
      import urllib.parse
      import requests
      
      gds_path = '/ROOT1/GDRIVE/VIDEO/방송중/교양/우리들의 지식살롱 (2024) [KBS LIFE]/우리들의 지식살롱.E10.240614.1080p-ST.mp4'
      
      # urllib.parse.quote_plus 사용
      url = f"{HOST}/gds_tool/api/fp/broadcast?gds_path={urllib.parse.quote_plus(gds_path)}&apikey={APIKEY}"
      result = requests.get(url).json()   
    
      # 또는 urllib.parse.urlencode 사용
      data = {
          "gds_path": gds_path,
          "apikey": APIKEY,
      }
      url = f"{HOST}/gds_tool/api/fp/broadcast?{urllib.parse.urlencode(data)}"
      result = requests.get(url).json()
  ```
