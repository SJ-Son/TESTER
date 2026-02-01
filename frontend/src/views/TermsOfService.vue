<template>
  <div class="h-full overflow-y-auto px-4 py-8 custom-scrollbar">
    <div class="max-w-3xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl relative">
      <h1 class="text-3xl font-bold text-white mb-6 border-b border-gray-800 pb-4">이용약관</h1>
      
      <div class="space-y-6 text-sm text-gray-400 leading-relaxed">
        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 1 조 (목적)</h2>
          <p>
            이 약관은 <strong>TESTER</strong>(이하 "서비스")가 제공하는 AI 테스트 코드 생성 서비스의 이용조건 및 절차, 
            서비스 운영자와 회원의 권리, 의무 및 책임사항 등 기타 필요한 사항을 규정함을 목적으로 합니다.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 2 조 (회원가입)</h2>
          <p>
            회원은 본 약관 및 개인정보처리방침에 동의하고, Google 계정을 연동함으로써 회원가입이 완료됩니다. 
            서비스는 별도의 비밀번호를 요구하지 않으며 Google 인증 시스템을 통해 신원을 확인합니다.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 3 조 (서비스의 제공)</h2>
          <p>
            본 서비스는 Google Gemini API를 활용하여 테스트 코드 생성 기능을 제공합니다. 
            AI가 생성한 코드의 정확성, 완전성, 무결성에 대해서는 보증하지 않습니다. 
            생성된 코드를 실제 운영 환경에 적용하여 발생하는 문제에 대한 책임은 사용자에게 있습니다.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 4 조 (회원의 의무 및 권리)</h2>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li>회원은 관계법령, 본 약관의 규정, 이용안내 및 서비스와 관련하여 공지한 주의사항을 준수해야 합니다.</li>
            <li>서비스의 UI, 로직 등 지식재산권은 운영자에게 귀속되나, <strong>서비스를 통해 생성된 결과물(테스트 코드)</strong>에 대한 권리는 <strong>회원에게 있으며, 이를 자유롭게 수정/배포/상업적으로 이용할 수 있습니다.</strong></li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 5 조 (책임의 한계)</h2>
          <p>
            본 서비스는 무료로 제공되는 서비스 이용과 관련하여 관련법에 특별한 규정이 없는 한 책임을 지지 않습니다. 
            또한, Google 로그인 서비스의 장애로 인한 서비스 이용 장애에 대해서는 책임을 지지 않습니다.
          </p>
        </section>
      </div>

      <div class="mt-10 pt-6 border-t border-gray-800 flex justify-center">
        <router-link to="/" class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium text-sm">
          홈으로 돌아가기
        </router-link>
      </div>
    </div>
  </div>
</template>
