블로그 포스트 자동 삽입용 이미지 폴더입니다.

파일: blog-01.jpg ~ blog-09.jpg (총 9장)

order.txt 사용법 (순환/셔플 방식, 완전 랜덤 아님):
- order.txt는 "다음에 쓸 이미지" 순서를 위에서부터 나열한 목록입니다.
- 새 글을 쓸 때마다 order.txt 맨 위 줄의 이미지 파일명을 하나 꺼내 쓰고, 그 줄을 order.txt에서 제거합니다.
- order.txt가 비면(9장을 모두 소진하면), blog-01.jpg~blog-09.jpg 9개 파일명을 다시 무작위로 섞어서 order.txt에 새로 채웁니다.
- 이렇게 하면 9장을 다 쓰기 전에는 같은 이미지가 반복되지 않습니다.

글에 삽입할 때는 각 article의 상단(<h2> 제목 바로 아래, <div class="prose"> 시작 전이나 첫 문단 위)에
<img src="images/blog/blog-XX.jpg" alt="키워드 관련 대체 텍스트" style="width:100%;border-radius:4px;margin:20px 0"> 형태로 넣습니다.
