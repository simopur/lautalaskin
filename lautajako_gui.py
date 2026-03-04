import tkinter as tk
from tkinter import messagebox, scrolledtext

class LautaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lautalaatikon Jakolaskin v1.4")
        self.root.geometry("550x750")
        
        # --- Syöttökentät (Päivitetyt lyhyet nimet) ---
        fields = [
            ("Laudan pituus mm", "4200"),
            ("ulkopituus mm", "12110"),
            ("tn etäisyys mm", "295"),
            ("tn väli mm", "960"),
            ("tn määrä kpl", "13")
        ]
        
        self.entries = {}
        for label_text, default_val in fields:
            frame = tk.Frame(root)
            frame.pack(pady=5, padx=20, fill='x')
            lbl = tk.Label(frame, text=label_text, width=25, anchor='w')
            lbl.pack(side='left')
            ent = tk.Entry(frame)
            ent.insert(0, default_val)
            ent.pack(side='right', expand=True, fill='x')
            self.entries[label_text] = ent

        # --- Painike päivetyllä tekstillä ---
        self.btn = tk.Button(root, text="Laske lautajako", command=self.laske, 
                             bg="#2ecc71", fg="white", font=('Arial', 10, 'bold'), pady=10)
        self.btn.pack(pady=20, padx=20, fill='x')

        tk.Label(root, text="Suunnitelma:").pack(anchor='w', padx=20)
        self.result_area = scrolledtext.ScrolledText(root, width=65, height=20)
        self.result_area.pack(pady=10, padx=20)

    def etsi_reitit(self, alkupiste, reitti, pituus, max_l, sallitut):
        if pituus - alkupiste <= max_l:
            return [reitti + [pituus]]
        
        loydetyt = []
        for sauma in sallitut:
            pala = sauma - alkupiste
            if 0 < pala <= max_l:
                tulokset = self.etsi_reitit(sauma, reitti + [sauma], pituus, max_l, sallitut)
                loydetyt.extend(tulokset)
        return loydetyt

    def laske(self):
        try:
            # Luetaan arvot uusilla kentän nimillä
            max_l = float(self.entries["Laudan pituus mm"].get())
            kokonais = float(self.entries["ulkopituus mm"].get())
            eka = float(self.entries["tn etäisyys mm"].get())
            vali = float(self.entries["tn väli mm"].get())
            maara = int(self.entries["tn määrä kpl"].get())

            # 1. Nostojen paikat
            nostot = [int(eka + (i * vali)) for i in range(maara) if (int(eka + (i * vali))) < kokonais]
            if len(nostot) < 3:
                messagebox.showerror("Virhe", "Trukkinostojen määrä on liian pieni.")
                return
            sallitut = nostot[1:-1]

            # 2. Etsi reitit
            kaikki_reitit = self.etsi_reitit(0, [0], kokonais, max_l, sallitut)
            if not kaikki_reitit:
                messagebox.showwarning("Huomio", "Jakoa ei löytynyt. Laudan pituus on liian lyhyt.")
                return

            # 3. Ryhmitellään ja valitaan parhaat
            reitit_koon_mukaan = {}
            for r in kaikki_reitit:
                koko = len(r)
                if koko not in reitit_koon_mukaan:
                    reitit_koon_mukaan[koko] = []
                reitit_koon_mukaan[koko].append(r)

            koot = sorted(reitit_koon_mukaan.keys())
            malli_a = reitit_koon_mukaan[koot[0]][0]
            malli_b = None
            
            for r in reitit_koon_mukaan[koot[0]]:
                if set(r[1:-1]) != set(malli_a[1:-1]):
                    malli_b = r
                    break
            
            if malli_b is None and len(koot) > 1:
                parhaat_b_ehdokkaat = reitit_koon_mukaan[koot[1]]
                malli_b = parhaat_b_ehdokkaat[len(parhaat_b_ehdokkaat)//2]

            # Tulostus
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, f"Ulkopituus: {int(kokonais)} mm | Laudan pituus: {int(max_l)} mm\n")
            self.result_area.insert(tk.END, "="*55 + "\n")
            self.tulosta_malli("MALLI A (Pohja)", malli_a)
            self.result_area.insert(tk.END, "\n" + "-"*55 + "\n")
            if malli_b:
                self.tulosta_malli("MALLI B (Sivut / Porrastettu)", malli_b)
            else:
                self.result_area.insert(tk.END, "Huom: Vain yksi toimiva jako löytyi.")

        except Exception as e:
            messagebox.showerror("Virhe", f"Tarkista syötteet: {e}")

    def tulosta_malli(self, nimi, reitti):
        palat = [int(reitti[i+1] - reitti[i]) for i in range(len(reitti)-1)]
        self.result_area.insert(tk.END, f"[{nimi}]\n")
        self.result_area.insert(tk.END, f"Kappaleita: {len(palat)} kpl\n")
        self.result_area.insert(tk.END, f"Laudat: {' + '.join(map(str, palat))} mm\n")
        self.result_area.insert(tk.END, f"Saumat (etäisyys alusta): {reitti[1:-1]} mm\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LautaApp(root)
    root.mainloop()