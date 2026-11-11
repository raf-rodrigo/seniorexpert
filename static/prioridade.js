// A prévia acompanha a regra de palavras inteiras aplicada no servidor.
const descricao = document.querySelector('textarea[name="descricao"]');
const prioridade = document.getElementById('prioridade');
const palavrasPrioritarias = /(?:^|[^\p{L}\p{N}_])(urgente|erro)(?=$|[^\p{L}\p{N}_])/iu;

function atualizarPrioridade() {
    prioridade.value = palavrasPrioritarias.test(descricao.value) ? 'Alta' : 'Normal';
}

descricao.addEventListener('input', atualizarPrioridade);
window.addEventListener('pageshow', atualizarPrioridade);
atualizarPrioridade();
