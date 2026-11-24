import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import weka.classifiers.AbstractClassifier;
import weka.classifiers.Classifier;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ConverterUtils.DataSource;

/** Fit a fixed archived binary classifier on each supplied OpenML training split. */
class RefitCredit {
    public static void main(String[] args) throws Exception {
        Instances data = new DataSource(args[0]).getDataSet();
        Instances splits = new DataSource(args[1]).getDataSet();
        data.setClass(data.attribute("class"));
        if (data.numInstances() != 1000 || data.numClasses() != 2) {
            throw new IllegalArgumentException("Expected the binary credit-g task");
        }
        Set<Integer> allTest = new HashSet<>();
        try (BufferedWriter output = Files.newBufferedWriter(Path.of(args[2]))) {
            output.write("fold,row_id,positive_class,probability,truth,predicted\n");
            for (int fold = 0; fold < 10; fold++) {
                Instances train = new Instances(data, 900);
                Set<Integer> trainRows = new HashSet<>();
                for (int j = 0; j < splits.numInstances(); j++) {
                    Instance s = splits.instance(j);
                    if (s.value(2) != 0) throw new IllegalArgumentException("Unexpected repeat");
                    if ((int)s.value(3) == fold && s.stringValue(0).equals("TRAIN")) {
                        int row = (int)s.value(1);
                        if (!trainRows.add(row)) throw new IllegalArgumentException("Duplicate train row");
                        train.add(data.instance(row));
                    }
                }
                if (train.numInstances() != 900) throw new IllegalArgumentException("Expected 900 training rows");
                Classifier model = AbstractClassifier.forName(args[3], Arrays.copyOfRange(args, 4, args.length));
                model.buildClassifier(train);
                int nTest = 0;
                for (int j = 0; j < splits.numInstances(); j++) {
                    Instance s = splits.instance(j);
                    if ((int)s.value(3) != fold || !s.stringValue(0).equals("TEST")) continue;
                    int row = (int)s.value(1);
                    if (trainRows.contains(row) || !allTest.add(row)) throw new IllegalArgumentException("Leaked or duplicate test row");
                    Instance labeled = data.instance(row);
                    String truth = labeled.stringValue(data.classIndex());
                    Instance test = (Instance) labeled.copy();
                    test.setClassMissing();
                    double[] prob = model.distributionForInstance(test);
                    int good = data.classAttribute().indexOfValue("good");
                    String pred = data.classAttribute().value(prob[0] >= prob[1] ? 0 : 1);
                    output.write(fold + "," + row + ",good," + prob[good] + "," + truth + "," + pred + "\n");
                    nTest++;
                }
                if (nTest != 100) throw new IllegalArgumentException("Expected 100 held-out rows");
            }
        }
        if (allTest.size() != data.numInstances()) throw new IllegalArgumentException("Incomplete pass");
    }
}
