"""Estilo y gráficos."""
import matplotlib.pyplot as plt

AZUL, NARANJA, GRIS, ROJO, NAVY = '#2a78d6', '#eb6834', '#8a8a86', '#e34948', '#14355F'


def estilo():
    plt.rcParams.update({
        'figure.figsize': (9, 4), 'figure.dpi': 110,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': True, 'axes.grid.axis': 'y', 'grid.alpha': 0.25, 'font.size': 11,
        'axes.titlesize': 12, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
    })


def grafico_azar(real, p, azar, titulo, mostrar=True):
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.hist(azar, bins=60, color=GRIS, edgecolor='white', linewidth=0.4, label='diferencias producidas por el azar')
    ax.axvline(real, color=NAVY, lw=2.5, label=f'diferencia real = {real:+.3f} R  (p = {p:.4f})')
    ax.set_ylim(0, ax.get_ylim()[1] * 1.35)
    ax.set_xlabel('diferencia de esperanza (R)')
    ax.set_title(titulo)
    ax.legend(frameon=False, loc='upper left', fontsize=9.5)
    if mostrar:
        plt.show()
    return fig
