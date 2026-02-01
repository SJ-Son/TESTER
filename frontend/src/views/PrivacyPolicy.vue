<template>
  <div class="h-full overflow-y-auto px-4 py-8 custom-scrollbar">
    <div class="max-w-3xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl relative">
      <h1 class="text-3xl font-bold text-white mb-6 border-b border-gray-800 pb-4">개인정보처리방침</h1>
      
      <div class="space-y-6 text-sm text-gray-400 leading-relaxed">
        <p>
          <strong>TESTER</strong>(이하 '서비스')는 정보주체의 자유와 권리 보호를 위해 「개인정보 보호법」 및 관계 법령이 정한 바를 준수하여, 
          적법하게 개인정보를 처리하고 안전하게 관리하고 있습니다.
        </p>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">1. 수집하는 개인정보의 항목</h2>
          <p>서비스는 회원가입 및 관리, 원활한 고충상담, 각종 서비스의 제공을 위해 'Google 로그인' 시 다음의 정보를 최소한으로 수집합니다.</p>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li><strong>필수항목</strong>: 이메일 주소, 이름(닉네임), 프로필 사진 URL, Google 사용자 고유 ID</li>
          </ul>
          <p class="mt-2 text-xs text-gray-500">* 본 서비스는 별도의 비밀번호를 수집하거나 저장하지 않습니다.</p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">2. 개인정보의 처리 목적</h2>
          <p>수집한 개인정보는 다음의 목적을 위해서만 처리합니다.</p>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li>서비스 이용에 따른 본인확인 및 회원 식별</li>
            <li>부정 이용 방지 및 비인가 사용 방지</li>
            <li>AI 테스트 코드 생성 기록 저장 및 열람 서비스 제공</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">3. 입력된 소스 코드의 처리 (중요)</h2>
          <p>
            사용자가 테스트 코드 생성을 위해 입력하는 <strong>소스 코드(Source Code)</strong>는 AI 분석 및 결과 생성을 위한 
            일시적인 목적(RAM)으로만 사용되며, <strong>서버나 데이터베이스에 영구적으로 저장되지 않습니다.</strong>
          </p>
          <div class="mt-2 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs">
            <p class="text-blue-400 font-semibold mb-1"> AI 학습 미이용 안내</p>
            <p>본 서비스는 사용자가 입력한 코드나 생성된 결과를 AI 모델(Gemini)의 학습용 데이터로 제공하거나 내부적으로 학습에 활용하지 않습니다.</p>
          </div>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">4. 개인정보 수탁업체 (Data Subprocessors)</h2>
          <p>서비스 제공을 위해 아래와 같은 외부 서비스를 이용하며, 해당 업체들은 각사의 개인정보 처리방침에 따라 데이터를 보호합니다.</p>
          <ul class="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Google Cloud (Gemini API)</strong>: AI 분석 및 코드 생성 서비스 제공</li>
            <li><strong>Cloudflare</strong>: 서비스 보안 및 봇 방지(Turnstile)</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">5. 국외 이전 및 보안</h2>
          <p>
            서비스의 특성상 Google 및 Cloudflare의 서버를 이용하며 데이터의 처리가 국외(Global)에서 이루어질 수 있습니다. 
            모든 데이터 전송은 암호화(HTTPS)를 통해 안전하게 보호됩니다.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-white mb-2">6. 개인정보의 파기</h2>
          <p>
            이용자의 개인정보는 원칙적으로 개인정보의 수집 및 이용목적이 달성되면 지체 없이 파기합니다. 
            회원 탈퇴 시 또는 서비스 종료 시 즉시 파기됩니다.
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
