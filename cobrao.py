import pygame
import random
import sys

#Inicialização do Pygame
pygame.init()

#Configs e Constante
LARGURA = 600
ALTURA = 400
TAMANHO_BLOCO = 20

# Paleta cor em RGB
COR_FUNDO = (30, 30, 30)
COR_COBRA = (46, 204, 113)
COR_COMIDA = (231, 76, 60)
COR_TEXTO = (236, 240, 241)

# Inic da janela principal
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake - Movimento Fluido (Lerp)")

# Controle de taxa de quadros e fonte para o texto
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("bahnschrift", 25)

def gerar_comida():
    """Sorteia uma posição aleatória para a comida alinhada à grade do jogo."""
    x = round(random.randrange(0, LARGURA - TAMANHO_BLOCO) / float(TAMANHO_BLOCO)) * TAMANHO_BLOCO
    y = round(random.randrange(0, ALTURA - TAMANHO_BLOCO) / float(TAMANHO_BLOCO)) * TAMANHO_BLOCO
    return [x, y]

def mostrar_hud(pontos, delay):
    """Renderiza a pontuação atual e o nível do jogador no topo da tela."""
    texto_pontos = fonte.render(f"Score: {pontos}", True, COR_TEXTO)
    nivel = int((100 - delay) / 2) + 1 
    texto_nivel = fonte.render(f"Level: {nivel}", True, COR_TEXTO) 
    tela.blit(texto_pontos, [10, 10])
    tela.blit(texto_nivel, [LARGURA - 110, 10])

def jogo():
    """Função principal contendo o loop do jogo, física, eventos e renderização."""
    game_over = False
    fim_de_jogo = False

    # Posição inicial da cabeça e vetores de velocidade
    x_cobra = LARGURA / 2
    y_cobra = ALTURA / 2
    delta_x = 0
    delta_y = 0

    # Estado da cobra (posições lógicas atuais e histórico do tick anterior para o Lerp)
    cabeca_inicial = [x_cobra, y_cobra]
    corpo_cobra = [cabeca_inicial]
    corpo_antigo =[cabeca_inicial] # Memória de onde a cobra estava no último tick lógico
    
    comprimento_cobra = 1
    posicao_comida = gerar_comida()

    # Configurações de tempo:
    # - fps_tela: Quantas vezes a tela redesenha por segundo (alta taxa = suavidade visual)
    # - delay_movimento: Intervalo em milissegundos entre as atualizações lógicas do jogo
    fps_tela = 120 
    delay_movimento = 100 
    tempo_ultimo_movimento = pygame.time.get_ticks()
    movimento_processado = True 

    #Loop Principal do Jogo
    while not game_over:

        # Game Over
        while fim_de_jogo:
            tela.fill(COR_FUNDO)
            msg1 = fonte.render("GAME OVER!", True, COR_COMIDA)
            msg2 = fonte.render("Pressione C para Continuar ou S para Sair", True, COR_TEXTO)
            
            tela.blit(msg1, [LARGURA / 2 - msg1.get_width() / 2, ALTURA / 3])
            tela.blit(msg2, [LARGURA / 2 - msg2.get_width() / 2, ALTURA / 2])
            
            mostrar_hud(comprimento_cobra - 1, delay_movimento)
            pygame.display.update()

            #comandos na tela de Game Over
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    game_over = True
                    fim_de_jogo = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_s:
                        game_over = True
                        fim_de_jogo = False
                    if evento.key == pygame.K_c:
                        jogo() # Reinicia a partida
                        return

        #Captura de Eventos de Entrada
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                game_over = True
            
            # Lê as setas do teclado impedindo giros de 180° e múltiplos comandos no mesmo tick
            if evento.type == pygame.KEYDOWN and movimento_processado:
                if evento.key == pygame.K_LEFT and delta_x == 0:
                    delta_x = -TAMANHO_BLOCO
                    delta_y = 0
                    movimento_processado = False
                elif evento.key == pygame.K_RIGHT and delta_x == 0:
                    delta_x = TAMANHO_BLOCO
                    delta_y = 0
                    movimento_processado = False
                elif evento.key == pygame.K_UP and delta_y == 0:
                    delta_y = -TAMANHO_BLOCO
                    delta_x = 0
                    movimento_processado = False
                elif evento.key == pygame.K_DOWN and delta_y == 0:
                    delta_y = TAMANHO_BLOCO
                    delta_x = 0
                    movimento_processado = False

        #Lógica de Atualização
        tempo_atual = pygame.time.get_ticks()
        
        # Só atualiza a matriz do jogo se tiver passado o tempo estipulado em `delay_movimento`
        if tempo_atual - tempo_ultimo_movimento >= delay_movimento:
            
            # Salva o estado visual do passo anterior (ponto A do Lerp)
            corpo_antigo = [segmento[:] for segmento in corpo_cobra]
            
            # Verifica colisão com as paredes
            if x_cobra >= LARGURA or x_cobra < 0 or y_cobra >= ALTURA or y_cobra < 0:
                fim_de_jogo = True

            # Avança a posição da cabeça no grid
            x_cobra += delta_x
            y_cobra += delta_y
            
            cabeca_cobra = [x_cobra, y_cobra]
            corpo_cobra.append(cabeca_cobra)

            # Gerencia a remoção da cauda antiga ou o crescimento
            if len(corpo_cobra) > comprimento_cobra:
                del corpo_cobra[0]
            elif len(corpo_antigo) > 0:
                # Duplica a cauda no snapshot para bater a contagem de blocos se a cobra crescer
                corpo_antigo.insert(0, corpo_antigo[0][:])

            # Verifica colisão com o próprio corpo
            for segmento in corpo_cobra[:-1]:
                if segmento == cabeca_cobra:
                    fim_de_jogo = True

            # Verifica colisão com a comida
            if x_cobra == posicao_comida[0] and y_cobra == posicao_comida[1]:
                posicao_comida = gerar_comida()
                comprimento_cobra += 1
                # Aumenta a velocidade do jogo reduzindo o delay (mínimo de 30ms)
                delay_movimento = max(30, 100 - ((comprimento_cobra - 1) * 2))

            tempo_ultimo_movimento = tempo_atual
            movimento_processado = True 

        #Renderização Gráfica com Lerp
        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_COMIDA, [posicao_comida[0], posicao_comida[1], TAMANHO_BLOCO, TAMANHO_BLOCO])
        
        # Calcula a porcentagem de tempo decorrido (0.0 a 1.0) entre o tick passado e o próximo
        progresso = (tempo_atual - tempo_ultimo_movimento) / delay_movimento
        if progresso > 1.0: progresso = 1.0

        # Para cada segmento, calcula a posição intermediária exata entre o Ponto A e Ponto B
        for i in range(len(corpo_cobra)):
            x_atual, y_atual = corpo_cobra[i][0], corpo_cobra[i][1]
            x_antigo, y_antigo = corpo_antigo[i][0], corpo_antigo[i][1]

            # Aplicação da Fórmula de Lerp: Pos_Antiga + (Diferença * Progresso)
            x_render = x_antigo + (x_atual - x_antigo) * progresso
            y_render = y_antigo + (y_atual - y_antigo) * progresso

            pygame.draw.rect(tela, COR_COBRA, [x_render, y_render, TAMANHO_BLOCO, TAMANHO_BLOCO])

        # Exibe o HUD e atualiza o frame na tela a 120 FPS
        mostrar_hud(comprimento_cobra - 1, delay_movimento)
        pygame.display.update()
        relogio.tick(fps_tela)

    # Finalização do programa
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    jogo()