import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import json
import os

class Arbre:
    def __init__(self, nom, taux_absorption):
        self.nom = nom
        self.taux_absorption = taux_absorption

class Jardin:
    def __init__(self):
        self.arbres = {}

    def ajouter_arbre(self, arbre):
        if arbre.nom in self.arbres:
            self.arbres[arbre.nom]['quantite'] += 1
        else:
            self.arbres[arbre.nom] = {'quantite': 1, 'arbre': arbre}

    def retirer_arbre(self, nom_arbre):
        if nom_arbre in self.arbres and self.arbres[nom_arbre]['quantite'] > 0:
            self.arbres[nom_arbre]['quantite'] -= 1
            if self.arbres[nom_arbre]['quantite'] == 0:
                del self.arbres[nom_arbre]

    def calculer_capture_totale(self):
        return sum(info['quantite'] * info['arbre'].taux_absorption for info in self.arbres.values())

    def obtenir_statistiques(self):
        total_arbres = sum(info['quantite'] for info in self.arbres.values())
        capture_totale = self.calculer_capture_totale()
        return {
            'total_arbres': total_arbres,
            'capture_totale': capture_totale,
            'arbres_par_type': {nom: info['quantite'] for nom, info in self.arbres.items()}
        }

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur de Capture de Carbone v3.0")
        self.geometry("1000x700")
        self.configure(bg='#f0f0f0')
        self.jardin = Jardin()
        self.arbres_disponibles = self.charger_arbres()
        
        self.creer_widgets()
        self.creer_frame_graphique()
        self.mettre_a_jour_affichage()

    def charger_arbres(self):
        if os.path.exists('arbres.json'):
            with open('arbres.json', 'r') as f:
                data = json.load(f)
                return {nom: Arbre(nom, info['taux_absorption']) for nom, info in data.items()}
        else:
            return {
                'Chêne': Arbre('Chêne', 22.0),
                'Érable': Arbre('Érable', 18.0),
                'Pin': Arbre('Pin', 20.0),
                'Saule': Arbre('Saule', 24.0),
                'Bouleau': Arbre('Bouleau', 19.0),
                'Hêtre': Arbre('Hêtre', 21.0),
                'Peuplier': Arbre('Peuplier', 23.0),
                'Tilleul': Arbre('Tilleul', 17.0),
                'Frêne': Arbre('Frêne', 20.5),
                'Orme': Arbre('Orme', 18.5)
            }

    def sauvegarder_arbres(self):
        data = {nom: {'taux_absorption': arbre.taux_absorption} 
                for nom, arbre in self.arbres_disponibles.items()}
        with open('arbres.json', 'w') as f:
            json.dump(data, f)

    def creer_widgets(self):
        self.creer_menu()
        self.creer_frame_principal()
        self.creer_footer()

    def creer_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        fichier_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Fichier", menu=fichier_menu)
        fichier_menu.add_command(label="Sauvegarder", command=self.sauvegarder_arbres)
        fichier_menu.add_command(label="Quitter", command=self.quit)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Ajouter un nouvel arbre", command=self.ajouter_nouvel_arbre)

    def creer_frame_principal(self):
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.choix_arbre = tk.StringVar()
        self.choix_arbre.set(list(self.arbres_disponibles.keys())[0])
        ttk.Label(frame, text="Type d'arbre:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.menu_arbres = ttk.Combobox(frame, textvariable=self.choix_arbre, values=list(self.arbres_disponibles.keys()))
        self.menu_arbres.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(frame, text="+", command=self.ajouter).grid(column=2, row=0, padx=5)
        ttk.Button(frame, text="-", command=self.retirer).grid(column=3, row=0, padx=5)

        self.texte_jardin = tk.StringVar()
        ttk.Label(frame, textvariable=self.texte_jardin, wraplength=400).grid(column=0, row=1, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(frame, text="Calculer la Capture de Carbone", command=self.calculer).grid(column=0, row=2, columnspan=4, sticky=(tk.W, tk.E), pady=10)

    def creer_frame_graphique(self):
        self.frame_graphique = ttk.Frame(self, padding="10")
        self.frame_graphique.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_graphique)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def creer_footer(self):
        footer = ttk.Frame(self, padding="5")
        footer.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        label = ttk.Label(footer, text="By MisterBra", cursor="hand2")
        label.pack(side=tk.RIGHT)
        label.bind("<Button-1>", lambda e: webbrowser.open('https://github.com/Misterbra'))

    def ajouter(self):
        arbre_selectionne = self.arbres_disponibles[self.choix_arbre.get()]
        self.jardin.ajouter_arbre(arbre_selectionne)
        self.mettre_a_jour_affichage()

    def retirer(self):
        self.jardin.retirer_arbre(self.choix_arbre.get())
        self.mettre_a_jour_affichage()

    def calculer(self):
        stats = self.jardin.obtenir_statistiques()
        message = f"""
        Statistiques du jardin:
        - Nombre total d'arbres: {stats['total_arbres']}
        - Capture totale de CO2: {stats['capture_totale']:.2f} kg/an

        Répartition des arbres:
        {self.formater_repartition_arbres(stats['arbres_par_type'])}
        """
        messagebox.showinfo("Statistiques de Capture de Carbone", message)

    def formater_repartition_arbres(self, arbres_par_type):
        return "\n".join(f"- {nom}: {quantite}" for nom, quantite in arbres_par_type.items())

    def mettre_a_jour_affichage(self):
        self.texte_jardin.set(f"Jardin actuel: {', '.join(f'{nom} ({info['quantite']})' for nom, info in self.jardin.arbres.items())}")
        self.mettre_a_jour_graphique()

    def mettre_a_jour_graphique(self):
        self.ax.clear()
        noms = list(self.jardin.arbres.keys())
        captures = [info['quantite'] * info['arbre'].taux_absorption for info in self.jardin.arbres.values()]
        
        if noms and captures:
            bars = self.ax.bar(noms, captures)
            self.ax.set_ylabel('Capture de CO2 (kg/an)')
            self.ax.set_title('Capture de CO2 par type d\'arbre')
            self.ax.tick_params(axis='x', rotation=45)
            
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{height:.1f}',
                             ha='center', va='bottom')
        else:
            self.ax.text(0.5, 0.5, 'Aucun arbre dans le jardin', ha='center', va='center')
        
        self.figure.tight_layout()
        self.canvas.draw()

    def ajouter_nouvel_arbre(self):
        nom = simpledialog.askstring("Nouvel arbre", "Nom de l'arbre:")
        if nom:
            taux = simpledialog.askfloat("Nouvel arbre", f"Taux d'absorption de CO2 pour {nom} (kg/an):")
            if taux is not None:
                self.arbres_disponibles[nom] = Arbre(nom, taux)
                self.menu_arbres['values'] = list(self.arbres_disponibles.keys())
                messagebox.showinfo("Succès", f"{nom} a été ajouté avec succès!")

if __name__ == "__main__":
    app = Application()
    app.mainloop()