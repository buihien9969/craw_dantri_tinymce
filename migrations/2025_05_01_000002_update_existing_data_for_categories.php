<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;
use App\Models\Category;
use App\Models\Article;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // Đánh dấu tất cả danh mục hiện tại là danh mục cha (parent_id = NULL)
        // Điều này đã được thiết lập mặc định trong migration thêm trường parent_id

        // Cập nhật ArticleVersion để thêm trường subcategory_id
        Schema::table('article_versions', function (Blueprint $table) {
            $table->unsignedBigInteger('subcategory_id')->nullable()->after('category_id');
            $table->foreign('subcategory_id')
                ->references('category_id')
                ->on('categories')
                ->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Xóa trường subcategory_id khỏi bảng article_versions
        Schema::table('article_versions', function (Blueprint $table) {
            $table->dropForeign(['subcategory_id']);
            $table->dropColumn('subcategory_id');
        });
    }
};
