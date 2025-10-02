import TokenReissuer from "@/components/TokenReissuer";

export default function TokenReissuePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            jQuants IDトークン管理
          </h1>
          <p className="text-gray-600">
            トークンの再発行と管理を行います
          </p>
        </div>
        
        <TokenReissuer />
        
        <div className="max-w-4xl mx-auto mt-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              📋 使用方法
            </h2>
            
            <div className="space-y-4 text-sm text-gray-700">
              <div>
                <h3 className="font-medium text-gray-900">1. 手動でのトークン再発行</h3>
                <p>上記のフォームを使用して、jQuantsの認証情報を入力し、トークンを再発行できます。</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900">2. コマンドラインでの再発行</h3>
                <div className="bg-gray-100 p-3 rounded-md font-mono text-xs">
                  <p># 仮想環境をアクティベート</p>
                  <p>source venv_token/bin/activate</p>
                  <p># トークン再発行スクリプトを実行</p>
                  <p>python3 reissue_jquants_token.py</p>
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900">3. 環境変数の設定</h3>
                <p>再発行後、以下の環境変数が自動的に設定されます：</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li><code>JQUANTS_EMAIL</code> - メールアドレス</li>
                  <li><code>JQUANTS_PASSWORD</code> - パスワード</li>
                  <li><code>JQUANTS_ID_TOKEN</code> - IDトークン</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
            <div className="flex items-start">
              <span className="text-yellow-600 text-lg mr-2">⚠️</span>
              <div>
                <h3 className="font-medium text-yellow-800">セキュリティに関する注意</h3>
                <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                  <li>• 認証情報は安全に管理してください</li>
                  <li>• .envファイルをGitにコミットしないでください</li>
                  <li>• トークンは24時間で期限切れになります</li>
                  <li>• 定期的なトークン更新を推奨します</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
