from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
from db import save_restaurant
from selenium.common.exceptions import NoSuchElementException
import random

def setup_chrome_driver():
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # WSL2에서 Chrome을 실행하기 위한 DISPLAY 환경변수 설정
    os.environ['DISPLAY'] = ':0'
    
    # Chrome 드라이버 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def main():
    # Chrome 드라이버 초기화
    driver = setup_chrome_driver()
    
    try:
        # 네이버 지도 URL로 이동
        url = "https://map.naver.com/p/entry/place/18635462?c=15.21,0,0,0,dh"
        driver.get(url)
        
        # 페이지가 완전히 로드될 때까지 대기
        driver.implicitly_wait(10)
        time.sleep(7)
        
        # 검색창 찾기 및 검색어 입력
        # 먼저 컨테이너 요소를 찾습니다
        search_container = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div")
        # 컨테이너 내부의 input 요소를 찾습니다
        search_input = search_container.find_element(By.TAG_NAME, "input")
        search_input.clear()
        search_input.send_keys("음식점")
        search_input.send_keys(Keys.RETURN)
        print("음식점 검색 완료")

        # 검색 결과가 로드될 때까지 대기
        time.sleep(5)
        
        # 지정된 경로의 요소를 찾아 텍스트 출력 및 클릭
        try:
            # iframe으로 전환
            iframe = driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
            driver.switch_to.frame(iframe)

            li_index = 0  # 시작 인덱스를 1로 설정 (line_num은 2부터 시작)
            page_num = 3  # 페이지 버튼 시작 번호
            last_height = 0
            
            # iframe 내부에서 요소 찾기 및 스크롤 처리
            while True:
                li_index += 1
                time.sleep(random.uniform(3, 5))
                try:
                    # 현재 스크롤 높이 저장
                    current_height = driver.execute_script("return document.body.scrollHeight")
                    
                    xpath = f"/html/body/div[3]/div/div[2]/div[1]/ul/li[{li_index}]"
                    try:
                        element = driver.find_element(By.XPATH, xpath)
                    except NoSuchElementException:
                        # 더 이상 요소가 없고 스크롤이 멈췄다면 다음 페이지 버튼 클릭
                        if current_height == last_height:
                            # 다음 페이지 버튼 클릭
                            next_page_xpath = f"/html/body/div[3]/div/div[2]/div[2]/a[{page_num}]"
                            try:
                                next_page_button = driver.find_element(By.XPATH, next_page_xpath)
                                next_page_button.click()
                                print(f"페이지 {page_num}로 이동했습니다.")
                                page_num += 1
                                li_index = 1  # 새 페이지에서는 인덱스 초기화
                                time.sleep(3)  # 페이지 로딩 대기
                                last_height = 0  # 스크롤 높이 초기화
                                continue
                            except NoSuchElementException:
                                print("마지막 페이지에 도달했습니다.")
                                break
                        else:
                            # 스크롤 더 내려보기
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            last_height = current_height
                            continue
                    
                    # 요소가 화면에 보이도록 스크롤
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(1)  # 스크롤 후 잠시 대기
                    
                    # 요소 클릭 및 처리
                    element.click()
                    
                    # 기본 컨텐츠로 돌아가기
                    driver.switch_to.default_content()
                    
                    # place/ 다음의 숫자 추출
                    match = re.search(r'place/(\d+)', driver.current_url)
                    if match:
                        place_id = match.group(1)
                        print(f"장소 ID: {place_id}")
                        
                        # DB에 장소 ID 저장 (line_num은 li_index + 1로 설정)
                        save_restaurant(place_id, line_num=li_index)
                    
                    # iframe으로 다시 전환하여 다음 항목 처리 준비
                    iframe = driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
                    driver.switch_to.frame(iframe)
                    
                    # 현재 스크롤 높이 업데이트
                    last_height = driver.execute_script("return document.body.scrollHeight")

                except Exception as e:
                    print(f"요소 {li_index}를 처리하는 중 오류 발생: {e}")
                    # iframe이 새로고침되었을 수 있으므로 다시 전환 시도
                    driver.switch_to.default_content()
                    iframe = driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
                    driver.switch_to.frame(iframe)


        except Exception as e:
            print(f"요소를 찾을 수 없습니다: {e}")

        time.sleep(30000)

    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        # 브라우저 종료
        driver.quit()

if __name__ == "__main__":
    main()