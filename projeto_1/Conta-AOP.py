"""
Sistema Bancário — OOP + AOP em Python puro
============================================
Paradigmas demonstrados:
  • Orientação a Objetos  → herança, encapsulamento, polimorfismo, abstração
  • Programação Orientada a Aspectos → log, autenticação, validação (via decorators)
 
Como executar:
  python banco_aop.py
"""
 
import functools
import time
import logging
from abc import ABC, abstractmethod
 
# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE LOG
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("BancoAOP")
 
SEP = "─" * 60
 
 
# ─────────────────────────────────────────────────────────────────────────────
# ASPECTOS TRANSVERSAIS (cross-cutting concerns)
# ─────────────────────────────────────────────────────────────────────────────
 
def aspecto_log(metodo):
    """Aspecto: registra TODA operação — @Before, @After e @AfterThrowing."""
    @functools.wraps(metodo)
    def wrapper(self, *args, **kwargs):
        classe = self.__class__.__name__
        nome   = metodo.__name__
        valor  = f"valor={args[0]:.2f}" if args else ""
 
        # @Before
        logger.info(f"[BEFORE] {classe}.{nome}({valor})")
        inicio = time.perf_counter()
 
        try:
            resultado = metodo(self, *args, **kwargs)
 
            # @After — sucesso
            elapsed = (time.perf_counter() - inicio) * 1000
            logger.info(f"[AFTER ] resultado={resultado:.2f}  tempo={elapsed:.3f}ms")
            return resultado
 
        except Exception as e:
            # @AfterThrowing
            logger.error(f"[ERROR ] {type(e).__name__}: {e}")
            raise
 
    return wrapper
 
 
def aspecto_autenticacao(metodo):
    """Aspecto: verifica se o usuário está autenticado antes de qualquer operação."""
    @functools.wraps(metodo)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "autenticado", False):
            raise PermissionError("Acesso negado: sessão inválida ou expirada.")
        return metodo(self, *args, **kwargs)
    return wrapper
 
 
def aspecto_validacao(metodo):
    """Aspecto: garante que o valor informado é positivo (ignorado em métodos sem 'valor')."""
    import inspect
    params = list(inspect.signature(metodo).parameters.keys())
    requer_valor = "valor" in params
 
    @functools.wraps(metodo)
    def wrapper(self, *args, **kwargs):
        if requer_valor and args:
            valor = args[0]
            if not isinstance(valor, (int, float)) or valor <= 0:
                raise ValueError(f"Valor inválido: {valor!r}. Deve ser um número positivo.")
        return metodo(self, *args, **kwargs)
    return wrapper
 
 
def aplicar_aspectos(cls):
    """
    Weaving: injeta os aspectos nas classes sem alterar seu código-fonte.
    Ordem de execução por chamada:
      autenticacao → validacao → log → método OOP
    """
    for nome in ("deposito", "saque", "consultar_saldo"):
        original = getattr(cls, nome, None)
        if original is None:
            continue
        # Empilhamento de decorators (interno → externo)
        decorado = aspecto_log(
                     aspecto_autenticacao(
                       aspecto_validacao(original)
                     )
                   )
        setattr(cls, nome, decorado)
    return cls
 
 
# ─────────────────────────────────────────────────────────────────────────────
# ORIENTAÇÃO A OBJETOS — hierarquia de classes
# ─────────────────────────────────────────────────────────────────────────────
 
class Conta(ABC):
    """Classe base abstrata. Define o contrato de qualquer conta bancária."""
 
    def __init__(self, titular: str, saldo_inicial: float = 0.0):
        self.titular     = titular
        self._saldo      = saldo_inicial   # encapsulamento
        self.autenticado = False
 
    def autenticar(self):
        self.autenticado = True
        logger.debug(f"Sessão autenticada para '{self.titular}'.")
 
    def encerrar_sessao(self):
        self.autenticado = False
        logger.debug(f"Sessão encerrada para '{self.titular}'.")
 
    # Método concreto compartilhado por todas as subclasses
    def consultar_saldo(self) -> float:
        return self._saldo
 
    @abstractmethod
    def deposito(self, valor: float) -> float: ...
 
    @abstractmethod
    def saque(self, valor: float) -> float: ...
 
    def __repr__(self):
        return f"{self.__class__.__name__}(titular={self.titular!r}, saldo={self._saldo:.2f})"
 
 
@aplicar_aspectos          # ← Weaving acontece aqui
class ContaCorrente(Conta):
    """
    Conta Corrente: permite saldo negativo até o limite do cheque especial.
    Herda: consultar_saldo
    Implementa: deposito, saque
    """
    LIMITE_CHEQUE_ESPECIAL = -500.0
 
    def deposito(self, valor: float) -> float:
        self._saldo += valor
        return self._saldo
 
    def saque(self, valor: float) -> float:
        if self._saldo - valor < self.LIMITE_CHEQUE_ESPECIAL:
            raise ValueError(
                f"Saldo insuficiente. Limite do cheque especial: "
                f"R$ {self.LIMITE_CHEQUE_ESPECIAL:.2f}"
            )
        self._saldo -= valor
        return self._saldo
 
 
@aplicar_aspectos          # ← Weaving acontece aqui
class ContaPoupanca(Conta):
    """
    Conta Poupança: aplica rendimento de 0,5% sobre depósitos.
    Herda: consultar_saldo
    Implementa: deposito, saque
    """
    TAXA_RENDIMENTO = 0.005  # 0,5% ao mês
 
    def deposito(self, valor: float) -> float:
        rendimento     = valor * self.TAXA_RENDIMENTO
        self._saldo   += valor + rendimento
        logger.debug(f"Rendimento aplicado: +R$ {rendimento:.2f}")
        return self._saldo
 
    def saque(self, valor: float) -> float:
        if valor > self._saldo:
            raise ValueError(
                f"Saldo insuficiente. Saldo atual: R$ {self._saldo:.2f}"
            )
        self._saldo -= valor
        return self._saldo
 
 
# ─────────────────────────────────────────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
 
def secao(titulo: str):
    print(f"\n{SEP}\n  {titulo}\n{SEP}")
 
 
def main():
    print("\n" + "═" * 60)
    print("  SISTEMA BANCÁRIO — OOP + AOP")
    print("═" * 60)
 
    # ── Instanciação (OOP) ────────────────────────────────────────
    secao("1. Criando contas")
    cc = ContaCorrente("Ana Silva",    saldo_inicial=1_000.0)
    cp = ContaPoupanca("Carlos Souza", saldo_inicial=2_500.0)
    print(f"  {cc}")
    print(f"  {cp}")
 
    # ── Operações normais ─────────────────────────────────────────
    secao("2. Conta Corrente — operações normais")
    cc.autenticar()
    cc.deposito(300.0)
    cc.saque(150.0)
    cc.consultar_saldo()
 
    secao("3. Conta Poupança — depósito com rendimento")
    cp.autenticar()
    cp.deposito(1_000.0)   # rendimento de 0,5% é aplicado
    cp.saque(200.0)
    cp.consultar_saldo()
 
    # ── Aspecto de autenticação ───────────────────────────────────
    secao("4. Tentativa sem autenticação (aspecto bloqueando)")
    cc.encerrar_sessao()
    try:
        cc.deposito(100.0)
    except PermissionError as e:
        print(f"  ✗ Bloqueado pelo aspecto: {e}")
 
    # ── Aspecto de validação ──────────────────────────────────────
    secao("5. Valor inválido (aspecto bloqueando)")
    cc.autenticar()
    try:
        cc.deposito(-50.0)
    except ValueError as e:
        print(f"  ✗ Bloqueado pelo aspecto: {e}")
 
    # ── Regra de negócio (OOP) ────────────────────────────────────
    secao("6. Conta Corrente — cheque especial excedido (regra OOP)")
    try:
        cc.saque(9_999.0)
    except ValueError as e:
        print(f"  ✗ Bloqueado pela regra de negócio: {e}")
 
    secao("7. Conta Poupança — saldo insuficiente (regra OOP)")
    try:
        cp.saque(99_999.0)
    except ValueError as e:
        print(f"  ✗ Bloqueado pela regra de negócio: {e}")
 
    # ── Estado final ──────────────────────────────────────────────
    secao("8. Estado final das contas")
    print(f"  {cc}")
    print(f"  {cp}")
    print()
 
 
if __name__ == "__main__":
    main()