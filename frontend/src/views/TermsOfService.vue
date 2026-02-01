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
          <h2 class="text-lg font-semibold text-white mb-2">제 3 조 (서비스의 제공 및 한계)</h2>
          <p>
            1. 본 서비스는 Google Gemini API를 활용하여 테스트 코드 자동 생성 기능을 제공합니다.<br>
            2. <strong>AI의 특성상 생성된 결과물에는 오류, 논리적 결함 혹은 비효율적인 코드가 포함될 수 있습니다(Hallucinations).</strong> 서비스는 결과물의 정확성, 안전성, 특정 목적에의 적합성을 보증하지 않습니다.<br>
            3. 사용자는 AI가 생성한 코드를 실제 환경에 적용하기 전 반드시 **보안 및 기능 검토**를 수행해야 하며, 이를 게을리하여 발생한 결과에 대한 책임은 사용자에게 있습니다.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 4 조 (금지사항)</h2>
          <p>회원은 서비스를 이용할 때 다음 각 호의 행위를 하여서는 안 됩니다.</p>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li>타인의 지식재산권을 침해하는 코드를 입력하는 행위</li>
            <li>악성코드 생성, 해킹, 타인에게 해를 끼칠 목적으로 서비스를 오용하는 행위</li>
            <li>자동화된 수단(봇, 스크래퍼 등)을 이용해 서비스에 과도한 부하를 주거나 리버싱을 시도하는 행위</li>
            <li>AI 모델의 취약점을 탐색하거나 부적절한 출력을 유도하는 행위 (Prompt Injection 등)</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 5 조 (회원의 권리와 책임)</h2>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li>서비스의 UI 및 로직에 대한 권리는 운영자에게 있습니다.</li>
            <li><strong>결과물에 대한 권리</strong>: 서비스를 통해 생성된 테스트 코드에 대한 권리는 <strong>해당 코드를 생성한 회원</strong>에게 있으며, 상업적 이용 및 배포가 자유롭습니다. 단, 원본 입력 코드에 대한 저작권 책임은 회원 본인에게 있습니다.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">제 6 조 (책임의 한계 및 면책)</h2>
          <p>
            운영자는 외부 서비스(Google Gemini, Cloudflare 등)의 장애, 천재지변 또는 이에 준하는 불가항력으로 인하여 서비스를 제공할 수 없는 경우에는 서비스 제공에 관한 책임이 면제됩니다.
            또한 무상으로 제공되는 서비스의 이용과 관련하여 이용자에게 발생한 손해에 대하여 책임을 지지 않습니다.
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
