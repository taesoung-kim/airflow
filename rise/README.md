1. 우리가 원하는 환경 : CeleryKubernetesExecutor
    - CeleryKubernetesExecutor airflow 3.0.0 부터 Deprecated 

2. bigdataquery는 api 형식으로 빼야될 것 같음
	- github-interface-server 처럼 api 기능하는 서버 생성
	- token 을 어떻게 interface할 것인가.
	- 그 외 함수는 어떻게 할 것인가... 가장 중요한것 setTimezone()
		- server를 kst로 띄우면 timezone 사용할일은 없을 것.


0. 테스트 해봐야 항목
	- 우선 log 없는 fail 이 생기지 않는 환경만들것
		- rise plugins 없는 환경
			- bigdataquery가 영향인가?
		- result backend 설정
			- 
		- redis sentinel (require replica write 0)
		- postgresql 보관주기 줄이기
	
	- 로그를 Volume에 저장하도록
	
    
